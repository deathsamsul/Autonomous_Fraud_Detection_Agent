from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd






ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)
rows = 500

base = pd.DataFrame({
    "merchant": rng.choice(["Amazon", "Target", "Walmart", "Ebay"], rows),
    "category": rng.choice(["shopping_net", "grocery_pos", "gas_transport"], rows),
    "amt": rng.uniform(1, 500, rows).round(2),
    "gender": rng.choice(["M", "F"], rows),
    "city": rng.choice(["New York", "Los Angeles", "Chicago"], rows),
    "state": rng.choice(["NY", "CA", "IL"], rows),
    "zip": rng.choice([10001, 90001, 60601], rows),
    "lat": rng.uniform(30, 45, rows),
    "long": rng.uniform(-120, -70, rows),
    "city_pop": rng.integers(1000, 8000000, rows),
    "job": rng.choice(["Engineer", "Doctor", "Teacher", "Student"], rows),
    "unix_time": rng.integers(1_300_000_000, 1_400_000_000, rows),
    "merch_lat": rng.uniform(30, 45, rows),
    "merch_long": rng.uniform(-120, -70, rows),
    "trans_date_trans_time": pd.date_range("2023-01-01", periods=rows, freq="h").astype(str),
    "dob": rng.choice(pd.date_range("1960-01-01", "2003-12-31", freq="D").astype(str), rows),
})

risk = (
    (base["amt"] > 350).astype(int)
    + (base["category"] == "shopping_net").astype(int)
    + (pd.to_datetime(base["trans_date_trans_time"]).dt.hour.isin([0, 1, 2, 3, 4])).astype(int)
)
prob = 1 / (1 + np.exp(-(risk - 1.5)))
base["is_fraud"] = (rng.random(rows) < prob).astype(int)

train = base.iloc[:400].copy()
test = base.iloc[400:].copy()

train.to_csv(DATA_DIR / "fraud_train.csv", index=False)
test.to_csv(DATA_DIR / "fraud_test.csv", index=False)
pd.DataFrame(columns=[
    "transaction_id", "timestamp", "fraud_probability", "prediction", "actual_label",
    "merchant", "category", "amt", "gender", "city", "state", "zip", "lat", "long",
    "city_pop", "job", "unix_time", "merch_lat", "merch_long", "trans_date_trans_time", "dob",
]).to_csv(DATA_DIR / "predictions.csv", index=False)

print("Sample data created in", DATA_DIR)
