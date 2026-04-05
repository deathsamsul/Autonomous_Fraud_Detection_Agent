from __future__ import annotations
from datetime import datetime, date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.inference.predictor import predict_fraud
from app.db.crud import insert_prediction, update_actual_label





app = FastAPI(title="Fraud Detection API", version="1.0.0")


class Transaction(BaseModel):
    merchant: str
    category: str
    amt: float
    gender: str
    city: str
    state: str
    zip: str
    lat: float
    long: float
    city_pop: int
    job: str
    unix_time: int
    merch_lat: float
    merch_long: float
    trans_date_trans_time: datetime
    dob: date


class LabelUpdate(BaseModel):
    transaction_id: str
    actual_label: int = Field(..., ge=0, le=1, description="Actual label must be 0 or 1")


@app.get("/")
def home():
    return { "message": "Hi, I am Samsul's fraud detection MLOps API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
def predict(transaction: Transaction):
    try:
        payload = transaction.model_dump()

        prediction, fraud_probability = predict_fraud(payload)

        transaction_id = insert_prediction(
            **payload,
            fraud_probability=fraud_probability,
            prediction=prediction
        )

        return {
            "transaction_id": str(transaction_id),
            "prediction": int(prediction),
            "fraud_probability": float(fraud_probability),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc # preserve the original exception traceback


@app.post("/update_label")
def update_label(payload: LabelUpdate):
    try:
        updated = update_actual_label(transaction_id=payload.transaction_id,
                                      actual_label=payload.actual_label )

        if not updated: # retued false 
            raise HTTPException(status_code=404, detail="Transaction ID not found")

        return {"message": "Label updated successfully","transaction_id": payload.transaction_id,
                "actual_label": payload.actual_label, }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

























# from __future__ import annotations
# import uuid
# from datetime import datetime, timezone
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field
# from app.inference.predictor import predict_fraud
# from app.utils.utility import append_prediction_to_csv, get_db_connection
# from app.db.crud import insert_prediction


# app = FastAPI(title="Fraud Detection API", version="1.0.0")

# # init_db()
# # init_csv()






# class Transaction(BaseModel):
#     merchant: str
#     category: str
#     amt: float
#     gender: str
#     city: str
#     state: str
#     zip: int
#     lat: float
#     long: float
#     city_pop: int
#     job: str
#     unix_time: int
#     merch_lat: float
#     merch_long: float
#     trans_date_trans_time: str
#     dob: str


# class LabelUpdate(BaseModel):
#     transaction_id: str
#     actual_label: int= Field(..., ge=0, le=1, description="Actual label must be 0 (legit) or 1 (fraud)")




# @app.get('/')
# def home():
#     return {'message':'hi iam samsul i agentic assistant for fraud detection mlops with automaed all tasks'}

# @app.get("/health")
# def health_check():
#     return {"status": "ok"}



# @app.post("/predict")
# def predict(transaction: Transaction):
#     try:
#         payload = transaction.model_dump()
#         prediction, fraud_probability = predict_fraud(payload)
#         insert_prediction(**payload, fraud_probability=fraud_probability, prediction=prediction)


#     except Exception as exc:
#         raise HTTPException(status_code=500, detail=str(exc)) from exc





#         # transaction_id = str(uuid.uuid4())
#         # timestamp = datetime.now(timezone.utc).isoformat()

#     #     with get_db_connection() as conn:
#     #         conn.execute(
#     #             "INSERT INTO predictions (transaction_id, timestamp, fraud_probability, prediction, actual_label) VALUES (?, ?, ?, ?, ?)",
#     #             (transaction_id, timestamp, fraud_probability, prediction, None),
#     #         )
#     #         conn.commit()

#     #     append_prediction_to_csv(
#     #         {
#     #             "transaction_id": transaction_id,
#     #             "timestamp": timestamp,
#     #             "fraud_probability": fraud_probability,
#     #             "prediction": prediction,
#     #             "actual_label": None,
#     #             **payload,
#     #         }
#     #     )

#     #     return {
#     #         "transaction_id": transaction_id,
#     #         "prediction": prediction,
#     #         "fraud_probability": fraud_probability,
#     #     }
#     # 

# @app.post("/update_label")
# def update_label(payload: LabelUpdate):
#     try:
#         with get_db_connection() as conn:
#             cursor = conn.execute(
#                 "UPDATE predictions SET actual_label = ? WHERE transaction_id = ?",
#                 (payload.actual_label, payload.transaction_id),
#             )
#             conn.commit()
#             if cursor.rowcount == 0:
#                 raise ValueError("Transaction ID not found")
#         return {"message": "Label updated successfully"}
#     except Exception as exc:
#         raise HTTPException(status_code=400, detail=str(exc)) from exc
