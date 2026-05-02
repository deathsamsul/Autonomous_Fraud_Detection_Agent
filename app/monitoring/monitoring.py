from __future__ import annotations
import json
import pandas as pd
from evidently.report import Report
from evidently.pipeline.column_mapping import ColumnMapping
from evidently.metric_preset import DataDriftPreset
# from evidently.metrics import ClassificationPresent
from sklearn.metrics import f1_score
from app.utils.utility import RAW_COLUMNS,PREDICTION_DATABASE_URL, METRICS_DB_URL, TRAINING_DATA_STORE_URL
from sqlalchemy import create_engine
from app.db.crud import insert_metrics


#  python -m app.bash_operator_scripts.monitor
# python -m app.monitoring.monitoring




def check_performance_drop(threshold_f1: float = 0.80) -> bool:

    try:  
        engine=create_engine(PREDICTION_DATABASE_URL)
        query = "SELECT * FROM transactions_predictions WHERE actual_label IS NOT NULL"
        df = pd.read_sql(query, engine)
       
        if len(df) < 10:
            return False

        f1 = f1_score(df["actual_label"].astype(int), df["prediction"].astype(int), zero_division=0)
        return bool(f1 < threshold_f1)
    except Exception:
        return False



def run_drift_detection(drift_threshold: float = 0.30) -> bool:

    try:
        engine=create_engine(TRAINING_DATA_STORE_URL)
        reference_df = pd.read_sql("SELECT * FROM fraud_training_data", engine)
        engine1=create_engine(PREDICTION_DATABASE_URL)
        current_df = pd.read_sql("SELECT * FROM transactions_predictions", engine1)

        if reference_df.empty:
            return False

        feature_cols = [col for col in RAW_COLUMNS if col in reference_df.columns and col in current_df.columns]
        if not feature_cols: # empty means false
            return False

        reference_df = reference_df.sample(min(len(reference_df), 2000), random_state=42)
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=reference_df[feature_cols], current_data=current_df[feature_cols])
        result = json.loads(report.json())  # json.load string → Python dictionary
        metric_data = result["metrics"][0]["value"]
        return bool(metric_data["share"] > drift_threshold)
    except Exception:
        return False



def run_monitoring_pipeline() -> bool:
    return bool(check_performance_drop() or run_drift_detection())
