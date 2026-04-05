from __future__ import annotations
import json
import os
import sqlite3
import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset
from sklearn.metrics import f1_score

from app.utils.utility import CSV_PATH, DB_PATH, RAW_COLUMNS, REFERENCE_DATA_PATH



def check_performance_drop(threshold_f1: float = 0.80, use_csv: bool = False) -> bool:
    try:
        if use_csv:
            if not CSV_PATH.exists():
                return False
            df = pd.read_csv(CSV_PATH)
            df = df[df["actual_label"].notna()]
        else:
            if not DB_PATH.exists():
                return False
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql("SELECT * FROM predictions WHERE actual_label IS NOT NULL", conn)
            conn.close()

        if len(df) < 10:
            return False

        f1 = f1_score(df["actual_label"].astype(int), df["prediction"].astype(int), zero_division=0)
        return bool(f1 < threshold_f1)
    except Exception:
        return False



def run_drift_detection(drift_threshold: float = 0.30) -> bool:
    try:
        if not REFERENCE_DATA_PATH.exists() or not CSV_PATH.exists():
            return False
        reference_df = pd.read_csv(REFERENCE_DATA_PATH)
        current_df = pd.read_csv(CSV_PATH)
        if reference_df.empty or current_df.empty:
            return False

        feature_cols = [col for col in RAW_COLUMNS if col in reference_df.columns and col in current_df.columns]
        if not feature_cols:
            return False

        reference_df = reference_df.sample(min(len(reference_df), 2000), random_state=42)
        report = Report(metrics=[DataDriftPreset()])
        report.run(reference_data=reference_df[feature_cols], current_data=current_df[feature_cols])
        result = json.loads(report.json())
        metric_data = result["metrics"][0]["value"]
        return bool(metric_data["share"] > drift_threshold)
    except Exception:
        return False



def run_monitoring_pipeline() -> bool:
    return bool(check_performance_drop() or run_drift_detection())
