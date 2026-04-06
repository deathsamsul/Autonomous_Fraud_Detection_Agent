from __future__ import annotations
from datetime import datetime, timezone
import mlflow
import mlflow.catboost
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from app.features.schema import load_and_preprocess_data
from sklearn.model_selection import train_test_split
from app.utils.utility import (MLFLOW_TRACKING_URI,EXPERIMENT_NAME,CATEGORICAL_COLS,TEMP_DIR,TRAINING_DATA_STORE_URL)
from sqlalchemy import create_engine
import os 
import pandas as pd


mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)



def train() -> dict:

#s3=boto3.client('s3',aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY,endpoint_url=ENDPOINT_URL)
    train_data_path=os.path.join(TEMP_DIR,"fraud_train.csv")
    engine=create_engine(TRAINING_DATA_STORE_URL)
    query="SELECT * FROM fraud_training_data"
    df=pd.read_sql(query,engine)
    df.to_csv(train_data_path,index=False)
 
    try:
        #s3.download_file('datasets', "fraud_train.csv", train_data_path)
        _,_,X, y = load_and_preprocess_data(train_data_path)

        X_train, X_valid, y_train, y_valid = train_test_split( X, y, test_size=0.2, random_state=42, stratify=y)

        params = {"iterations": 300,"learning_rate": 0.1,"depth": 6,"loss_function": "Logloss",
                "eval_metric": "AUC","random_seed": 42,"verbose": 0,}

        with mlflow.start_run(run_name="train_candidate") as run:
            mlflow.log_params(params)
            model = CatBoostClassifier(**params)
            model.fit(X_train,y_train,cat_features=CATEGORICAL_COLS,eval_set=(X_valid, y_valid),use_best_model=True,
                    verbose=False,)

            pred_proba = model.predict_proba(X_valid)[:, 1]
            roc_auc = float(roc_auc_score(y_valid, pred_proba))
            mlflow.log_metric("roc_auc", roc_auc)
            mlflow.catboost.log_model(model, artifact_path="model")
            # mlflow.catboost.log_model(model, artifact_="model")   # "model" is the artifact path in mlflow

            os.remove(train_data_path)
            return {"run_id": run.info.run_id,"roc_auc": roc_auc,"trained_at": datetime.now(timezone.utc).isoformat(),}
        
    finally:
         if os.path.exists(train_data_path):
            os.remove(train_data_path)


if __name__ == "__main__":
    print(train())





