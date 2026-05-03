import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any
import pandas as pd
from sqlalchemy import create_engine,text
import psycopg2




## CREATE USER prediction_user WITH PASSWORD 'predict123';
METRICS_DB_URL=os.environ.get("METRICS_DB_URL") or "postgresql+psycopg2://metrics:metrics123@localhost:5432/appdata"
PREDICTION_DATABASE_URL=os.environ.get("PREDICTION_DATABASE_URL") or "postgresql+psycopg2://prediction_user:predict123@localhost:5432/appdata"
TRAINING_DATA_STORE_URL=os.environ.get("TRAINING_DATA_STORE_URL") or "postgresql+psycopg2://training_user:train123@localhost:5432/appdata"
# DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@localhost:5432/{your_database}"
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")
MODEL_NAME="fraud_detection_model"
ENDPOINT_URL=os.environ.get("ENDPOINT_URL", "http://127.0.0.1:9000")  # MinIO endpoint URL
BUCKET_NAME=os.environ.get("BUCKET_NAME", "models")  # MinIO bucket
AWS_ACCESS_KEY_ID=os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin")
DATABASE_URL = "postgresql://mlflow:mlflow1@localhost:5432/mlflowdb"
EXPERIMENT_NAME = "fraud_detection"
MONITORING_EXPERIMENT_NAME = "fraud_monitoring"
CATEGORICAL_COLS = ["merchant", "category", "gender", "city", "state", "job"]
BASE_DIR = Path(__file__).resolve().parents[2]
# TEMP_DIR = BASE_DIR / "temp_data"
TEMP_DIR = Path( os.environ.get("TEMP_DIR", BASE_DIR / "temp_data"))
os.makedirs(TEMP_DIR, exist_ok=True)



MODEL_COLUMNS = ["merchant", "category", "amt", "gender", "city", "state", "zip", "lat",
                 "long", "city_pop", "job", "unix_time", "merch_lat", "merch_long",
                 "hour", "day", "month", "weekday", "age", "distance", "amt_log",
                   "is_night", "is_weekend"]



RAW_COLUMNS = [ "merchant", "category", "amt", "gender", "city", "state", "zip", "lat", "long",
                "city_pop", "job", "unix_time", "merch_lat", "merch_long", "trans_date_trans_time", "dob"]


PREDICTION_COLUMNS = ["transaction_id", "timestamp", "fraud_probability", "prediction", "actual_label",*RAW_COLUMNS,]

CATEGORICAL_COLS = ['merchant', 'category', 'gender', 'city', 'state', 'job']




def upload_training_data_to_db(data_path: str) -> None:
    engine = create_engine(TRAINING_DATA_STORE_URL)

    df = pd.read_csv(data_path)
    RAW_COLUMN = [ "merchant", "category", "amt", "gender", "city", "state", "zip", "lat", "long",
                "city_pop", "job", "unix_time", "merch_lat", "merch_long", "trans_date_trans_time", "dob", "is_fraud"]
    df = df[RAW_COLUMN]
    df.rename(columns={"is_fraud": "actual_label"}, inplace=True)




    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE fraud_training_data"))
        conn.commit()

    df.to_sql("fraud_training_data",engine,schema="public",if_exists="append",index=False)  # if_exists table not exist create else append






#before upload use trancate
#TRUNCATE TABLE fraud_training_data;


# GRANT SELECT, INSERT, DELETE, TRUNCATE
# ON fraud_training_data
# TO training_user;
# CREATE USER training_user WITH PASSWORD 'train123';
# CREATE USER prediction_user WITH PASSWORD 'predict123';

# CREATE TABLE fraud_training_data (

#     merchant TEXT,
#     category TEXT,
#     amt NUMERIC(12,2),
#     gender TEXT,
#     city TEXT,
#     state TEXT,
#     zip TEXT,
#     lat DOUBLE PRECISION,
#     long DOUBLE PRECISION,
#     city_pop BIGINT,
#     job TEXT,
#     unix_time BIGINT,
#     merch_lat DOUBLE PRECISION,
#     merch_long DOUBLE PRECISION,
#     trans_date_trans_time TIMESTAMP,
#     dob DATE,

#     actual_label INTEGER CHECK (actual_label IN (0,1))

# );


# CREATE TABLE transactions_predictions (

#     transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
#     timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

#     fraud_probability DOUBLE PRECISION,
#     prediction INTEGER CHECK (prediction IN (0,1)),
#     actual_label INTEGER CHECK (actual_label IN (0,1)),

#     merchant TEXT,
#     category TEXT,
#     amt NUMERIC(12,2),
#     gender TEXT,
#     city TEXT,
#     state TEXT,
#     zip TEXT,
#     lat DOUBLE PRECISION,
#     long DOUBLE PRECISION,
#     city_pop BIGINT,
#     job TEXT,
#     unix_time BIGINT,
#     merch_lat DOUBLE PRECISION,
#     merch_long DOUBLE PRECISION,
#     trans_date_trans_time TIMESTAMP,
#     dob DATE
# );














# DATA_DIR = Path(os.environ.get("DATA_DIR", BASE_DIR / "data"))
# DB_DIR = Path(os.environ.get("DB_DIR", BASE_DIR / "database"))
# MODELS_DIR = Path(os.environ.get("MODELS_DIR", BASE_DIR / "models"))
# LOGS_DIR = Path(os.environ.get("LOGS_DIR", BASE_DIR / "logs"))
# MLFLOW_DIR = Path(os.environ.get("MLFLOW_DIR", BASE_DIR / "mlruns"))
# DB_PATH = Path(os.environ.get("DB_PATH", DB_DIR / "fraud_monitor.db"))
# CSV_PATH = Path(os.environ.get("CSV_PATH", DATA_DIR / "predictions.csv"))
# TRAIN_DATA_PATH = Path(os.environ.get("TRAIN_DATA_PATH", DATA_DIR / "fraud_train.csv"))
# REFERENCE_DATA_PATH = Path(os.environ.get("REFERENCE_DATA_PATH", TRAIN_DATA_PATH))
# PRODUCTION_MODEL_PATH = Path(os.environ.get("PRODUCTION_MODEL_PATH", MODELS_DIR / "production_model.cbm"))
# CANDIDATE_MODEL_PATH = Path(os.environ.get("CANDIDATE_MODEL_PATH", MODELS_DIR / "candidate_model.cbm"))
# REGISTRY_PATH = Path(os.environ.get("REGISTRY_PATH", MODELS_DIR / "registry.json"))










# def ensure_dirs() -> None:
#     for path in [DATA_DIR, DB_DIR, MODELS_DIR, LOGS_DIR, MLFLOW_DIR]:
#         path.mkdir(parents=True, exist_ok=True)


# @contextmanager
# def get_db_connection() -> Any:
#     ensure_dirs()
#     conn = sqlite3.connect(DB_PATH)
#     try:
#         yield conn
#     finally:
#         conn.close()



# def init_db() -> None:
#     ensure_dirs()
#     with get_db_connection() as conn:
#         conn.execute(
#             """
#             CREATE TABLE IF NOT EXISTS predictions (
#                 transaction_id TEXT PRIMARY KEY,
#                 timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
#                 fraud_probability REAL,
#                 prediction INTEGER,
#                 actual_label INTEGER
#             )
#             """
#         )
#         conn.commit()



# def init_csv() -> None:
#     ensure_dirs()
#     if not CSV_PATH.exists():
#         pd.DataFrame(columns=PREDICTION_COLUMNS).to_csv(CSV_PATH, index=False)



# def append_prediction_to_csv(record: dict) -> None:
#     ensure_dirs()
#     df = pd.DataFrame([record])
#     df.to_csv(CSV_PATH, mode="a", header=not CSV_PATH.exists(), index=False)



# def update_label_in_csv(transaction_id: str, actual_label: int) -> None:
#     if not CSV_PATH.exists():
#         raise FileNotFoundError(f"Prediction CSV not found: {CSV_PATH}")
#     df = pd.read_csv(CSV_PATH)
#     if transaction_id not in df["transaction_id"].values:
#         raise ValueError(f"Transaction ID {transaction_id} not found in CSV")
#     df.loc[df["transaction_id"] == transaction_id, "actual_label"] = actual_label
#     df.to_csv(CSV_PATH, index=False)



# def load_predictions_from_csv() -> pd.DataFrame:
#     if CSV_PATH.exists():
#         return pd.read_csv(CSV_PATH)
#     return pd.DataFrame(columns=PREDICTION_COLUMNS)



# def write_registry(data: dict) -> None:
#     ensure_dirs()
#     with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
#         json.dump(data, f, indent=2)



# def read_registry() -> dict:
#     if not REGISTRY_PATH.exists():
#         return {}
#     with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
#         return json.load(f)


# #mlflow.set_tracking_uri("http://localhost:5000")

# # #model registry
# # import boto3
# # import mlflow
# # import mlflow.sklearn
# # import pandas as pd

# # # Download dataset
# # s3 = boto3.client(
# #     "s3",
# #     endpoint_url="http://127.0.0.1:9000",
# #     aws_access_key_id="minioadmin",
# #     aws_secret_access_key="minioadmin"
# # )

# # s3.download_file(
# #     "datasets",
# #     "fraud_train.csv",
# #     "/tmp/fraud_train.csv"
# # )

# # # Train
# # df = pd.read_csv("/tmp/fraud_train.csv")
# # model = train_model(df)

# # # MLflow logging
# # with mlflow.start_run():

# #     mlflow.log_param("model", "fraud_detection")

# #     mlflow.sklearn.log_model(
# #         model,
# #         "model",
# #         registered_model_name="fraud_detection_model"
# #     )



# # # move to production 
# # from mlflow.tracking import MlflowClient

# # client = MlflowClient()

# # client.transition_model_version_stage(
# #     name="fraud_detection_model",
# #     version=1,
# #     stage="Production"
# # )