import os
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

TRAINING_DATA_STORE_URL = os.environ.get(
    "TRAINING_DATA_STORE_URL",
    "postgresql+psycopg2://training_user:train123@postgres-cluster-rw.database.svc.cluster.local:5432/appdata")

DATA_DIR = Path(os.environ.get("DATA_DIR", "/opt/datasets"))


# def upload_training_data_to_db(data_path: str) -> None:

#     engine = create_engine(TRAINING_DATA_STORE_URL)
#     df = pd.read_csv(data_path)

#     raw_columns = [
#         "merchant", "category", "amt", "gender", "city", "state", "zip",
#         "lat", "long", "city_pop", "job", "unix_time", "merch_lat",
#         "merch_long", "trans_date_trans_time", "dob", "is_fraud"]

#     df = df[raw_columns]
#     df.rename(columns={"is_fraud": "actual_label"}, inplace=True)

#     df.to_sql(
#         "training_data",
#         engine,
#         if_exists="replace",
#         index=False)

#     print(f"Uploaded {len(df)} rows to training_data table")


def upload_training_data_to_db(data_path: str) -> None:
    engine = create_engine(TRAINING_DATA_STORE_URL)

    df = pd.read_csv(data_path)

    raw_columns = [
        "merchant", "category", "amt", "gender", "city", "state", "zip",
        "lat", "long", "city_pop", "job", "unix_time", "merch_lat",
        "merch_long", "trans_date_trans_time", "dob", "is_fraud"
    ]

    df = df[raw_columns]
    df.rename(columns={"is_fraud": "actual_label"}, inplace=True)

    df["trans_date_trans_time"] = pd.to_datetime(df["trans_date_trans_time"])
    df["dob"] = pd.to_datetime(df["dob"]).dt.date
    df["zip"] = df["zip"].astype(str)

    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE public.fraud_training_data"))

    df.to_sql(
        "fraud_training_data",
        engine,
        schema="public",
        if_exists="append",
        index=False
    )

    print(f"Uploaded {len(df)} rows to public.fraud_training_data")


if __name__ == "__main__":
    data_path = DATA_DIR / "fraud_train_data.csv"

    if not data_path.exists():
        raise FileNotFoundError(f"Training data not found: {data_path}")

    upload_training_data_to_db(str(data_path))



# docker run \
#   -v $(pwd)/datasets:/opt/datasets \
#   -e TRAINING_DATA_STORE_URL="postgresql+psycopg2://training_user:train123@postgres-cluster-rw.database.svc.cluster.local:5432/appdata" \
#   image

#   python app/startup_jobs/store_train_data.py
#  python3 -m app.startup_jobs.store_train_data