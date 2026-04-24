from __future__ import annotations
import pandas as pd
import streamlit as st
from app.utils.utility import load_predictions_from_csv

# INCOMPLETED


st.set_page_config(page_title="Fraud Monitoring Dashboard", layout="wide")
st.title("Fraud Monitoring Dashboard")

df = load_predictions_from_csv()
if df.empty:
    st.info("No predictions in CSV yet.")
    st.stop()

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

col1, col2, col3 = st.columns(3)
col1.metric("Total Predictions", len(df))
col2.metric("Predicted Fraud", int(df["prediction"].fillna(0).sum()))
col3.metric("Avg Fraud Probability", round(float(df["fraud_probability"].fillna(0).mean()), 4))

st.subheader("Recent Predictions")
st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)

if "timestamp" in df.columns and df["timestamp"].notna().any():
    ts = df.copy()
    ts["date"] = ts["timestamp"].dt.date
    daily = ts.groupby("date").size().reset_index(name="count")
    st.subheader("Daily Prediction Volume")
    st.line_chart(daily.set_index("date"))
