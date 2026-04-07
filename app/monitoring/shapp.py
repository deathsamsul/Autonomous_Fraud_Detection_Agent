from app.features.schema import try_prepare_features_for_shap
import shap
import pandas as pd
import numpy as np
from sklearn.metrics import (accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,confusion_matrix)





# drift detection helper
def compute_simple_drift(reference_df: pd.DataFrame, current_df: pd.DataFrame): 

    result = {"status": "Unavailable","drifted_features": [],"total_features": 0,"drift_score": 0.0,}
    
    if reference_df.empty or current_df.empty:
        return result

    common_cols = [c for c in reference_df.columns if c in current_df.columns]
    if not common_cols:
        return result

    drifted = []
    for col in common_cols:
        ref = reference_df[col].dropna()
        cur = current_df[col].dropna()

        if len(ref) == 0 or len(cur) == 0:    # If any dataset is empty → cannot compute drift
            continue

        # numeric drift
        if pd.api.types.is_numeric_dtype(ref) and pd.api.types.is_numeric_dtype(cur): # api is submodule of pandas for type checking
            ref_mean = ref.mean()
            cur_mean = cur.mean()
            ref_std = ref.std()

            if pd.isna(ref_std) or ref_std == 0:
                ref_std = 1e-9

            shift = abs(cur_mean - ref_mean) / abs(ref_std)
            if shift > 0.5:
                drifted.append((col, round(float(shift), 3)))

        else:
            ref_top = ref.astype(str).value_counts(normalize=True)  # percentage distribution
            cur_top = cur.astype(str).value_counts(normalize=True)
  # ref_top.index → the categories in order of frequency:

            ref_top_cat = ref_top.index[0] if len(ref_top) > 0 else None
            ref_top_pct = ref_top.iloc[0] if len(ref_top) > 0 else 0.0
            cur_top_pct = cur_top.get(ref_top_cat, 0.0) if ref_top_cat is not None else 0.0

            diff = abs(cur_top_pct - ref_top_pct)
            if diff > 0.3:
                drifted.append((col, round(float(diff), 3)))

    total_features = len(common_cols)
    drift_score = len(drifted) / total_features if total_features > 0 else 0.0
    result["drifted_features"] = drifted
    result["total_features"] = total_features
    result["drift_score"] = drift_score
    result["status"] = "Drift Detected" if len(drifted) > 0 else "No Drift"

    return result


# shap explanation helper
def explain_with_shap(model, raw_row: pd.DataFrame):
    
    x_prepared, err = try_prepare_features_for_shap(raw_row)
    if err is not None:
        return None, f"Feature engineering failed: {err}"

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(x_prepared)

        # CatBoost / tree models may return list for binary classification
        if isinstance(shap_values, list):
            sv = shap_values[1][0]
        else:
            sv = shap_values[0]

        shap_df = pd.DataFrame({"feature": x_prepared.columns,"shap_value": sv}).sort_values("shap_value", key=np.abs,
                                                                                              ascending=False)
        return {"prepared_row": x_prepared,"shap_df": shap_df}, None

    except Exception as e:
        return None, f"SHAP explanation failed: {e}"
    
# metrics computation helper
def compute_metrics(data: pd.DataFrame):
    metrics = {"labeled_count": 0,"accuracy": None,"precision": None,"recall": None,"f1": None,"roc_auc": None,"cm": None}

    labeled_df = data[data["actual_label"].notna()].copy()
    metrics["labeled_count"] = len(labeled_df)

    if labeled_df.empty:
        return metrics

    y_true = labeled_df["actual_label"].astype(int)
    y_pred = labeled_df["prediction"].astype(int)

    metrics["accuracy"] = accuracy_score(y_true, y_pred)
    metrics["precision"] = precision_score(y_true, y_pred, zero_division=0)
    metrics["recall"] = recall_score(y_true, y_pred, zero_division=0)
    metrics["f1"] = f1_score(y_true, y_pred, zero_division=0)
    metrics["cm"] = confusion_matrix(y_true, y_pred)

    if "fraud_probability" in labeled_df.columns and y_true.nunique() == 2:
        metrics["roc_auc"] = roc_auc_score(y_true, labeled_df["fraud_probability"])

    return metrics