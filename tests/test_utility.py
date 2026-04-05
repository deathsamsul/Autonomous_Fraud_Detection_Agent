import os

import pandas as pd
import pytest

from app.utils import utility as util


@pytest.fixture(autouse=True)
def override_paths(monkeypatch, tmp_path):
    temp_db_dir = tmp_path / "database"
    temp_csv_dir = tmp_path / "data"
    temp_models_dir = tmp_path / "models"
    temp_db_dir.mkdir(parents=True, exist_ok=True)
    temp_csv_dir.mkdir(parents=True, exist_ok=True)
    temp_models_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(util, "DB_DIR", temp_db_dir)
    monkeypatch.setattr(util, "DATA_DIR", temp_csv_dir)
    monkeypatch.setattr(util, "MODELS_DIR", temp_models_dir)
    monkeypatch.setattr(util, "DB_PATH", temp_db_dir / "test_fraud_monitor.db")
    monkeypatch.setattr(util, "CSV_PATH", temp_csv_dir / "test_predictions.csv")


def test_db_init():
    util.init_db()
    assert os.path.exists(util.DB_PATH)



def test_db_insert_and_select():
    util.init_db()
    with util.get_db_connection() as conn:
        conn.execute(
            "INSERT INTO predictions (transaction_id, fraud_probability, prediction) VALUES (?, ?, ?)",
            ("txn123", 0.75, 1),
        )
        conn.commit()
        cursor = conn.execute("SELECT * FROM predictions WHERE transaction_id = ?", ("txn123",))
        row = cursor.fetchone()
        assert row is not None
        assert row[0] == "txn123"
        assert row[2] == 0.75
        assert row[3] == 1



def test_csv_init():
    util.init_csv()
    assert os.path.exists(util.CSV_PATH)
    df = pd.read_csv(util.CSV_PATH)
    assert df.empty
