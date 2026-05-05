from __future__ import annotations
from datetime import datetime, date
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field
from prometheus_client import (Counter,Gauge,Histogram,generate_latest,CONTENT_TYPE_LATEST,)
from app.inference.predictor import predict_fraud
from app.db.crud import insert_prediction, update_actual_label
import logging




logger = logging.getLogger(__name__)
app = FastAPI(title="Fraud Detection API", version="1.0.0")




# prometheus Metrics --------------------------------------------
# count every HTTP request
REQUEST_COUNT = Counter("api_requests_total","Total number of API requests",["method", "endpoint", "http_status"],)
# measure API request latency 
REQUEST_LATENCY = Histogram("api_request_duration_seconds","Time spent processing API requests",["method", "endpoint"],)
# count prediction endpoint calls
PREDICT_REQUEST_COUNT = Counter("fraud_predict_requests_total","Total number of prediction requests",)
# count prediction errors
PREDICT_ERROR_COUNT = Counter("fraud_predict_errors_total","Total number of prediction errors",)
# latest fraud probability from most recent prediction
LATEST_FRAUD_PROBABILITY = Gauge("fraud_latest_probability","Fraud probability from the latest prediction",)
# count fraud predictions
FRAUD_PREDICTION_COUNT = Counter("fraud_predictions_total","Total number of fraud predictions",)
# count non-fraud predictions
NON_FRAUD_PREDICTION_COUNT = Counter("non_fraud_predictions_total","Total number of non-fraud predictions",)
# count label updates
LABEL_UPDATE_COUNT = Counter("fraud_label_updates_total","Total number of actual label updates",)
# count label update errors
LABEL_UPDATE_ERROR_COUNT = Counter("fraud_label_update_errors_total","Total number of label update errors",)
HIGH_RISK_PREDICTION_COUNT = Counter("fraud_high_risk_predictions_total","Total number of high risk predictions")

# middleware for all routes
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):  #function that calls actual endpoint 
    start_time = time.time()
    status_code = 500 # default 
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        status_code = 500
        raise
    finally:    # this use to record metrics even if an exception occurs, ensuring we capture all requests
        duration = time.time() - start_time
        path = request.url.path

        
        if path != "/metrics":
            REQUEST_COUNT.labels( method=request.method,endpoint=path,http_status=str(status_code),).inc()

            REQUEST_LATENCY.labels(method=request.method,endpoint=path,).observe(duration)


# validation models for API endpoints 
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




# API endpoints
@app.get("/")
def home():
    return {"message": "Hi, I am Samsul's fraud detection MLOps API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
def predict(transaction: Transaction):
    PREDICT_REQUEST_COUNT.inc()

    try:
        payload = transaction.model_dump()
        prediction, fraud_probability = predict_fraud(payload)

        transaction_id = insert_prediction(**payload,fraud_probability=fraud_probability,prediction=prediction,)

        # update gauge with latest probability
        LATEST_FRAUD_PROBABILITY.set(float(fraud_probability))

        # count fraud vs non-fraud
        if int(prediction) == 1:
            FRAUD_PREDICTION_COUNT.inc()
        else:
            NON_FRAUD_PREDICTION_COUNT.inc()

        if float(fraud_probability) >= 0.80:
            HIGH_RISK_PREDICTION_COUNT.inc()

        return { "transaction_id": str(transaction_id),"prediction": int(prediction),
                "fraud_probability": float(fraud_probability),}

    except Exception as exc:
        logger.exception("Error during prediction: %s", exc)
        PREDICT_ERROR_COUNT.inc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/update_label")
def update_label(payload: LabelUpdate):
    try:
        updated = update_actual_label( transaction_id=payload.transaction_id, actual_label=payload.actual_label,)

        if not updated:
            raise HTTPException(status_code=404, detail="Transaction ID not found")

        LABEL_UPDATE_COUNT.inc()

        return { "message": "Label updated successfully", "transaction_id": payload.transaction_id,
                "actual_label": payload.actual_label,}

    except HTTPException:  # expected HTTP exceptions (like 404) like transaaction not found 
        raise
    except Exception as exc:    # unexpected exceptions (like database errors) should be counted 
                                          #   as label update errors and return a 400 
        LABEL_UPDATE_ERROR_COUNT.inc()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
