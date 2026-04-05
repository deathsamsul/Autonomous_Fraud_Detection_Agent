from __future__ import annotations
import pandas as pd
from app.features.schema import feature_engineering
from app.utils.utility import CATEGORICAL_COLS





def load_and_preprocess_data(path: str):
    df = pd.read_csv(path)
    if "is_fraud" not in df.columns:
        raise ValueError("Training/evaluation dataset must contain 'is_fraud'")

    # y = df["is_fraud"].astype(int)
    y = df["is_fraud"].str.lower().map({"yes": 1, "no": 0})    
    X = feature_engineering(df)

    for col in CATEGORICAL_COLS:
        X[col] = X[col].astype(str)

    return X, y



# def prepare_single_record(record: dict) -> pd.DataFrame:
#     df = pd.DataFrame([record])
#     X = feature_engineering(df)
#     for col in CATEGORICAL_COLS:
#         X[col] = X[col].astype(str)
#     return X
