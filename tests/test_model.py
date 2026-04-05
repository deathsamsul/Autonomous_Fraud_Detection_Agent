from unittest.mock import patch

import numpy as np

from app.inference.predictor import predict_fraud


class DummyModel:
    def predict(self, X):
        return np.array([1] * len(X))

    def predict_proba(self, X):
        return np.array([[0.2, 0.8]] * len(X))



def test_predict_fraud():
    with patch("app.inference.predictor.get_model") as mock_get_model:
        mock_get_model.return_value = DummyModel()
        input_data = {
            "merchant": "fraud_Kirlin and Sons",
            "category": "shopping_net",
            "amt": 2500.75,
            "gender": "M",
            "city": "Los Angeles",
            "state": "CA",
            "zip": 90001,
            "lat": 34.0522,
            "long": -118.2437,
            "city_pop": 4000000,
            "job": "Doctor",
            "unix_time": 1371816917,
            "merch_lat": 36.1699,
            "merch_long": -115.1398,
            "trans_date_trans_time": "2023-01-01 02:30:00",
            "dob": "1985-05-15",
        }
        pred, prob = predict_fraud(input_data)
        assert pred == 1
        assert prob == 0.8
