from __future__ import annotations
import numpy as np
import pandas as pd
from app.utils.utility import MODEL_COLUMNS, RAW_COLUMNS, CATEGORICAL_COLS



def _ensure_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")





def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    _ensure_columns(data, RAW_COLUMNS)

    data["trans_date_trans_time"] = pd.to_datetime(data["trans_date_trans_time"], errors="coerce")
    data["dob"] = pd.to_datetime(data["dob"], errors="coerce")

    if data["trans_date_trans_time"].isna().any():
        raise ValueError("Invalid values in trans_date_trans_time")
    if data["dob"].isna().any():
        raise ValueError("Invalid values in dob")

    data["hour"] = data["trans_date_trans_time"].dt.hour
    data["day"] = data["trans_date_trans_time"].dt.day
    data["month"] = data["trans_date_trans_time"].dt.month
    data["weekday"] = data["trans_date_trans_time"].dt.weekday
    data["age"] = ((data["trans_date_trans_time"] - data["dob"]).dt.days / 365.25).clip(lower=0).fillna(0)
    data["distance"] = np.sqrt((data["lat"] - data["merch_lat"]) ** 2 + (data["long"] - data["merch_long"]) ** 2)
    data["amt_log"] = np.log1p(data["amt"].clip(lower=0))
    data["is_night"] = data["hour"].isin([22, 23, 0, 1, 2, 3, 4]).astype(int)
    data["is_weekend"] = data["weekday"].isin([5, 6]).astype(int)

    for col in MODEL_COLUMNS:
        if col not in data.columns:
            raise ValueError(f"Engineered feature missing: {col}")

    return data[MODEL_COLUMNS].copy()


def get_target(df):

    if "is_fraud" in df.columns:
        return df["is_fraud"]

    elif "actual_label" in df.columns:
        return df["actual_label"]

    else:
        raise ValueError("Target column not found")

def load_and_preprocess_data(path: str):

# LATER USE NEW PREDICTED  DATA FOR VALIDATION WITH SAME TIME BASED SPLIT
    df = pd.read_csv(path)
    # sorting data by time to validate model on recent data
    df = df.sort_values("trans_date_trans_time").reset_index(drop=True)

    target = get_target(df)

    if target.dtype == "object":
        Y = target.str.lower().map({"yes": 1, "no": 0}).astype(int)
    else:
        Y = target.astype(int)
        
    X = feature_engineering(df)

    for col in CATEGORICAL_COLS:
        X[col] = X[col].astype(str)

# validation on recent 3000 records and rest for training
    x_valid=X.iloc[-3000:]
    y_valid=Y.iloc[-3000 :]
    # remaining records for training
    x_train=X.iloc[:-3000]
    y_train=Y.iloc[:-3000]

    return x_valid, y_valid, x_train, y_train






def try_prepare_features_for_shap(raw_df: pd.DataFrame):
      
    try:
        prepared = feature_engineering(raw_df.copy())
        return prepared, None
    except Exception as e:
        return None, e
