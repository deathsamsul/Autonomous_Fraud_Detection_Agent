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






# import datetime
# import json

# from sqlalchemy import (
#     create_engine,
#     Column,
#     Integer,
#     String,
#     Float,
#     DateTime,
#     JSON
# )

# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker

# from evidently import Report, ColumnMapping
# from evidently.metrics import ClassificationPreset


# # PostgreSQL connection
# DATABASE_URL = "postgresql://postgres:password@localhost:5432/prediction_db"

# engine = create_engine(DATABASE_URL)

# Session = sessionmaker(bind=engine)
# session = Session()

# Base = declarative_base()


# # Model Metrics Table
# class ModelMetrics(Base):
#     __tablename__ = "model_metrics"

#     id = Column(Integer, primary_key=True)

#     model_name = Column(String)
#     model_version = Column(String)

#     accuracy = Column(Float)
#     precision = Column(Float)
#     recall = Column(Float)
#     f1_score = Column(Float)

#     metrics = Column(JSON)

#     created_at = Column(DateTime, default=datetime.datetime.utcnow)


# # Create table first time
# Base.metadata.create_all(engine)


# # Column mapping
# column_mapping = ColumnMapping(
#     target="target",
#     prediction="prediction"
# )


# # Run Evidently
# report = Report(metrics=[ClassificationPreset()])

# report.run(
#     reference_data=reference_df,
#     current_data=current_df,
#     column_mapping=column_mapping
# )


# # Extract metrics
# metrics_dict = report.as_dict()


# # Extract important values
# classification_metrics = metrics_dict["metrics"][0]["result"]

# accuracy = classification_metrics.get("accuracy")
# precision = classification_metrics.get("precision")
# recall = classification_metrics.get("recall")
# f1 = classification_metrics.get("f1")


# # Store in PostgreSQL
# record = ModelMetrics(
#     model_name="fraud_model",
#     model_version="v1",

#     accuracy=accuracy,
#     precision=precision,
#     recall=recall,
#     f1_score=f1,

#     metrics=metrics_dict
# )

# session.add(record)
# session.commit()

# session.close()

# print("Metrics stored successfully")