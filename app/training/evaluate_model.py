from __future__ import annotations
from app.utils.utility import MLFLOW_TRACKING_URI,ENDPOINT_URL, AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY,TEMP_DIR
import mlflow
from catboost import CatBoostClassifier
from sklearn.metrics import f1_score,precision_score,recall_score,roc_auc_score
import boto3
from app.mlops.mlflow_utils import load_production_model
from app.features.data_processing import load_and_preprocess_data
import pandas as pd
import os
import shutil






mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)




def _calculate_metrics(model:CatBoostClassifier ,x,y)-> dict:
    pred=model.predict(x)
    proba=model.predict_proba(x)[:,1]
    return {"roc_auc":float(roc_auc_score(y,proba)),"f1":float(f1_score(y,pred,zero_division=0)),
            "precision":float(precision_score(y,pred,zero_division=0)),
            "recall":float(recall_score(y,pred,zero_division=0)),}





def evaluate_candidate_model(candidate_run_id: str, min_roc_auc: float = 0.80, max_recall_drop: float = 0.22):
    
    client = mlflow.MlflowClient()


    s3=boto3.client("s3",endpoint_url=ENDPOINT_URL,aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    
    test_file_path=os.path.join(TEMP_DIR,"fraud_test.csv")
    s3.download_file('datasets','fraud_test.csv',test_file_path)  
    x_test, y_test = load_and_preprocess_data(test_file_path)

    candidate_model_uri = f"runs:/{candidate_run_id}/model"
    candidate_model = mlflow.catboost.load_model(candidate_model_uri)
    candidate_metrics = _calculate_metrics(candidate_model, x_test, y_test)

    production_metrics = { "roc_auc": 0.0,"f1": 0.0,"precision": 0.0,"recall": 0.0,}

    try:
        prod_model = load_production_model()
        if prod_model: # model exists,then exicute calculate metrics
            production_metrics = _calculate_metrics(prod_model, x_test, y_test)

    except Exception as e:
        print(f"Could not evaluate production model: {e}")

   # decision logic based on metrics comparison and thresholds
    passed = True
    reasons = []

    if candidate_metrics["roc_auc"] <= min_roc_auc:
        passed = False
        reasons.append(f"Candidate ROC AUC {candidate_metrics['roc_auc']:.4f} below minimum threshold {min_roc_auc:.4f}")

    if candidate_metrics["roc_auc"] <= production_metrics["roc_auc"]:
        passed = False
        reasons.append(
            f"Candidate ROC AUC {candidate_metrics['roc_auc']:.4f} is not better than production ROC AUC {production_metrics['roc_auc']:.4f}"
        )

    if candidate_metrics["recall"] < production_metrics["recall"] - max_recall_drop:
        passed = False
        reasons.append(
            f"Candidate recall {candidate_metrics['recall']:.4f} dropped too much from production recall {production_metrics['recall']:.4f}"
        )

    result = {"passed": passed,"candidate_run_id": candidate_run_id,"candidate_metrics": candidate_metrics,
              "production_metrics": production_metrics,"reasons": reasons if reasons else ["Candidate passed to evaluation"],}

    print("Evaluation result:")
    print(result)

    # shutil.rmtree(f'{temp_dir}/fraud_test.csv')
    os.remove(test_file_path)

    return result










