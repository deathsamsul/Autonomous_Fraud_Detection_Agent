from __future__ import annotations
from app.mlops.mlflow_utils import load_production_model
import pandas as pd
from app.utils.utility import CATEGORICAL_COLS
from app.features.schema import feature_engineering



_model=None

def get_model():
    global _model
    if _model is None:
        _model = load_production_model()
    return _model




def predict_fraud(input_data: dict):
    
    model = get_model()

    try:
        df = pd.DataFrame([input_data])
        df = feature_engineering(df)
        for col in CATEGORICAL_COLS:
            df[col] = df[col].astype(str)
        
        pred = model.predict(df)[0]
        proba= model.predict_proba(df)[0][1]
        return int(pred), float(proba)
    except Exception as e:
        raise ValueError(f"Error occurred while making prediction: {e}")    

