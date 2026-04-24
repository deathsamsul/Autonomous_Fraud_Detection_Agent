import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests
from app.monitoring.shapp import compute_metrics,explain_with_shap,compute_simple_drift
import matplotlib.pyplot as plt
from app.utils.utility import TRAINING_DATA_STORE_URL,PREDICTION_DATABASE_URL,MODEL_COLUMNS
from app.monitoring.shapp import compute_metrics,compute_simple_drift,explain_with_shap
from app.inference.predictor import get_model
from sqlalchemy import create_engine



# streamlit run app/monitoring/monitoring_dashbord.py


# page config
st.set_page_config(page_title="Fraud Monitoring", layout="wide")
st.title(" Fraud Detection Monitoring Dashboard")
st.write("Track fraud trends, evaluate model quality, monitor drift, explain risky predictions, "
         "and capture analyst feedback for continuous improvement.")



def show_metric_card(label, value, help_text=None):
    st.metric(label, value, help=help_text)



@st.cache_resource
def load_model_once():
    try:
        return get_model()
    except Exception as e:
        return e



# df = load_predictions_from_csv()
engine=create_engine(PREDICTION_DATABASE_URL)
try:
    df=pd.read_sql("SELECT * FROM transactions_predictions", con=engine)
    if "transaction_id" in df.columns:
        df["transaction_id"] = df["transaction_id"].astype(str)
except Exception as e:
    st.error(f"Error loading predictions from database: {e}")
    st.stop()

st.sidebar.header("Filters")

if df.empty:
    st.info("No predictions in CSV yet.")
    st.stop()

df = df.copy()
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.dropna(subset=["timestamp"])
min_date = df["timestamp"].dt.date.min()
max_date = df["timestamp"].dt.date.max()

date_range = st.sidebar.date_input("Date range", [min_date, max_date])

if len(date_range) == 2:
    start_date, end_date = date_range
    df = df[(df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)]

prediction_filter = st.sidebar.multiselect("Prediction filter",options=[0, 1],default=[0, 1])
df = df[df["prediction"].isin(prediction_filter)]

prob_range = st.sidebar.slider("Fraud probability range",min_value=0.0,max_value=1.0,value=(0.0, 1.0),step=0.01)
df = df[(df["fraud_probability"] >= prob_range[0]) &(df["fraud_probability"] <= prob_range[1])]

if df.empty:
    st.warning("No records found for selected filters.")
    st.stop()

df["date"] = df["timestamp"].dt.date


# KPI selection and display/Key Performance Indicator
total = len(df)
fraud_pred = int((df["prediction"] == 1).sum())
legit_pred = int((df["prediction"] == 0).sum())
fraud_rate = fraud_pred / total if total > 0 else 0
avg_prob = df["fraud_probability"].mean() if total > 0 else 0

metrics = compute_metrics(df)
labeled_count = metrics["labeled_count"]

st.subheader(" System Overview")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    show_metric_card("Total Predictions", f"{total}", "Total transactions scored by the model")
with col2:
    show_metric_card("Pred Fraud", f"{fraud_pred}", "Transactions predicted as fraud")
with col3:
    show_metric_card("Pred Legit", f"{legit_pred}", "Transactions predicted as non-fraud")
with col4:
    show_metric_card("Fraud Rate", f"{fraud_rate:.2%}", "Share of predictions marked as fraud")
with col5:
    show_metric_card("Avg Probability", f"{avg_prob:.2%}", "Average model fraud score")
with col6:
    show_metric_card("Labeled", f"{labeled_count}", "Rows with analyst-confirmed labels")


# ALERTS
st.subheader(" Alerts")

alerts = []

if fraud_rate > 0.30:   # later increase threshold or make dynamic based on historical fraud rates
    alerts.append(f"High fraud rate detected: {fraud_rate:.2%}")

if labeled_count < 20:
    alerts.append("Very little labeled data available. Performance metrics may be unstable.")

if metrics["recall"] is not None and metrics["recall"] < 0.60:
    alerts.append(f"Recall is low ({metrics['recall']:.2%}). The model may be missing fraud cases. need to tigger retrain pipeline ")

if metrics["precision"] is not None and metrics["precision"] < 0.60:
    alerts.append(f"Precision is low ({metrics['precision']:.2%}). Too many false alerts may be happening.")

if alerts:
    for a in alerts:
        st.warning(a)
else:
    st.success("System looks stable for the selected time window.")


# model performance evaluation
st.subheader(" Model Metrics")
st.caption(
    "Accuracy = overall correctness, Precision = fraud alert correctness, "
    "Recall = how many real frauds are caught, F1 = balance of precision and recall, "
    "ROC-AUC = how well the model separates fraud from non-fraud."
)

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    st.metric("Accuracy", f"{metrics['accuracy']:.2%}" if metrics["accuracy"] is not None else "N/A")
with m2:
    st.metric("Precision", f"{metrics['precision']:.2%}" if metrics["precision"] is not None else "N/A")
with m3:
    st.metric("Recall", f"{metrics['recall']:.2%}" if metrics["recall"] is not None else "N/A")
with m4:
    st.metric("F1-score", f"{metrics['f1']:.2%}" if metrics["f1"] is not None else "N/A")
with m5:
    st.metric("ROC-AUC", f"{metrics['roc_auc']:.3f}" if metrics["roc_auc"] is not None else "N/A")

if metrics["cm"] is not None:
    st.markdown("**Confusion Matrix**")
    cm_df = pd.DataFrame( metrics["cm"],index=["Actual Legit", "Actual Fraud"],columns=["Pred Legit", "Pred Fraud"])
    fig_cm = px.imshow(cm_df, text_auto=True, aspect="auto", title="Confusion Matrix")
    st.plotly_chart(fig_cm, use_container_width=True)
else:
    st.info("No labeled data available yet, so confusion matrix and performance metrics are limited.")


# drift detection
st.subheader(" Drift Detection")
engine1=create_engine(TRAINING_DATA_STORE_URL)
query = "SELECT * FROM fraud_training_data"
try:
    reference_df = pd.read_sql(query, con=engine1)
except Exception as e:
    st.error(f"Error loading training data from database: {e}")
    st.stop()

# reference_df = safe_read_csv(TRAIN_DATA_PATH)

# Try to compare on shared columns only
current_df = df.copy()

# remove obvious non-feature monitoring columns if present
ignore_cols = ["transaction_id", "timestamp", "date", "prediction", "fraud_probability", "actual_label"]
reference_features = reference_df.drop(columns=[c for c in ignore_cols if c in reference_df.columns], errors="ignore")
current_features = current_df.drop(columns=[c for c in ignore_cols if c in current_df.columns], errors="ignore")

drift_result = compute_simple_drift(reference_features, current_features)

d1, d2, d3 = st.columns(3)

with d1:
    st.metric("Drift Status", drift_result["status"])
with d2:
    st.metric("Drifted Features", f"{len(drift_result['drifted_features'])}/{drift_result['total_features']}")
with d3:
    st.metric("Drift Score", f"{drift_result['drift_score']:.2%}")

if drift_result["status"] == "Drift Detected":
    st.warning("Feature distribution shift detected. Retraining may be needed.")
else:
    st.success("No major drift detected in the selected data window.")

if drift_result["drifted_features"]:
    drift_df = pd.DataFrame(drift_result["drifted_features"], columns=["feature", "drift_value"])
    fig_drift = px.bar(drift_df.sort_values("drift_value", ascending=False),x="feature",y="drift_value",title="Drifted Features")
    st.plotly_chart(fig_drift, use_container_width=True)
else:
    st.info("No drifted features identified by the current simple drift check.")


st.subheader(" Monitoring Trends")

left, right = st.columns(2)

with left:
    volume_ts = df.groupby("date").size().reset_index(name="count")
    fig1 = px.line(volume_ts, x="date", y="count", markers=True, title="Daily Prediction Volume")
    st.plotly_chart(fig1, use_container_width=True)

with right:
    fraud_ts = df.groupby("date")["prediction"].mean().reset_index(name="fraud_rate")
    fig2 = px.line(fraud_ts, x="date", y="fraud_rate", markers=True, title="Daily Fraud Rate")
    fig2.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader(" Fraud Probability Distribution")
fig3 = px.histogram(df, x="fraud_probability", nbins=40, title="Fraud Probability Histogram")
fig3.add_vline(x=0.5, line_dash="dash", annotation_text="Threshold")
st.plotly_chart(fig3, use_container_width=True)


# high risk transactions
st.subheader(" High-Risk Transactions")

high_risk_df = df[df["fraud_probability"] >= 0.80].copy()
high_risk_df = high_risk_df.sort_values("fraud_probability", ascending=False)

if high_risk_df.empty:
    st.info("No high-risk transactions found.")
else:
    st.dataframe(high_risk_df[ ["transaction_id", "timestamp", "fraud_probability", "prediction", "actual_label"] ].head(50),
                  use_container_width=True)


# SHAP explanations
st.subheader(" Explainable AI (SHAP)")
st.caption(
    "SHAP explains why a transaction was flagged by showing which features pushed the prediction toward fraud or non-fraud.")

model_obj = load_model_once()

if isinstance(model_obj, Exception):
    st.info(f"Model could not be loaded for SHAP explanation: {model_obj}")
else:
    explain_source_df = high_risk_df if not high_risk_df.empty else df.sort_values("fraud_probability", ascending=False)
    available_txns = explain_source_df["transaction_id"].astype(str).head(50).tolist()

    if available_txns:
        selected_shap_txn = st.selectbox("Select transaction for explanation",options=available_txns,key="shap_txn_selector")
        raw_row = explain_source_df[explain_source_df["transaction_id"].astype(str) == str(selected_shap_txn)].head(1)

        if not raw_row.empty:
            explanation, error = explain_with_shap(model_obj, raw_row)

            if error is not None:
                st.warning(error)
                st.info(
                    "Make sure your `feature_engineering()` accepts a raw dataframe row and returns "
                    "the same model-ready columns used during training.")
                
            else:
                shap_df = explanation["shap_df"].copy()

                top_n = st.slider("Top SHAP features to display", 5, 20, 10)

                top_shap = shap_df.head(top_n).copy()
                top_shap["impact"] = np.where(top_shap["shap_value"] >= 0, "Increase Fraud Risk", "Decrease Fraud Risk")

                fig_shap = px.bar(top_shap.sort_values("shap_value"),x="shap_value",y="feature",color="impact",orientation="h",
                                  title="Top Feature Contributions for Selected Transaction")
                st.plotly_chart(fig_shap, use_container_width=True)

                st.markdown("**Top explanation summary**")
                for _, row in top_shap.head(5).iterrows():
                    direction = "increased" if row["shap_value"] >= 0 else "decreased"
                    st.write(f"- `{row['feature']}` {direction} fraud risk (SHAP={row['shap_value']:.4f})")


# recent predictions and label update
st.subheader(" Recent Predictions")

recent_df = df.sort_values("timestamp", ascending=False).copy()

st.dataframe(recent_df[["transaction_id", "timestamp", "fraud_probability", "prediction", "actual_label"]].head(100),
             use_container_width=True)

csv_data = recent_df.to_csv(index=False).encode("utf-8")
st.download_button(label="Download filtered data as CSV",data=csv_data,
                   file_name="fraud_monitoring_filtered.csv",mime="text/csv")


# label update form
st.subheader(" Update Actual Label")
st.caption("Analyst feedback improves monitoring quality and future retraining.")

txn_options = recent_df["transaction_id"].astype(str).head(100).tolist()

with st.form("label_update_form"):
    selected_txn_id = st.selectbox("Select Transaction ID", options=txn_options)

    current_row = recent_df[recent_df["transaction_id"].astype(str) == str(selected_txn_id)].head(1)

    if not current_row.empty:
        st.write(f"**Prediction:** {int(current_row['prediction'].iloc[0])}")
        st.write(f"**Fraud Probability:** {float(current_row['fraud_probability'].iloc[0]):.2%}")
        st.write(f"**Current Actual Label:** {current_row['actual_label'].iloc[0]}")

    true_label = st.selectbox("New Actual Label", [0, 1])
    submitted = st.form_submit_button("Update Label")

    if submitted:
        try:
            response = requests.post("http://127.0.0.1:8000/update_label",json={"transaction_id": selected_txn_id,
                                                                                "actual_label": true_label },timeout=10 )
            if response.status_code == 200:
                st.success(f"Label for {selected_txn_id} updated to {true_label}")
                st.rerun()
            else:
                try:
                    st.error(response.json().get("detail", "Failed to update label"))
                except Exception:
                    st.error("Failed to update label")

        except requests.exceptions.RequestException as e:
            st.error(f"API connection error: {e}")