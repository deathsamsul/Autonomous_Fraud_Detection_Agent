from app.utils.utility import MLFLOW_TRACKING_URI, MODEL_NAME
from catboost import CatBoostClassifier
import mlflow.catboost



mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

# load model from mlflow registry
def load_production_model() -> CatBoostClassifier:
    client=mlflow.MlflowClient()
    try :
        latest_version = client.get_latest_versions(MODEL_NAME, stages=["Production"])[0]
        if not latest_version:
            raise RuntimeError("no production model found. Train and register a model first.")
        model_uri=f"models:/{MODEL_NAME}/{latest_version.version}"
        model=mlflow.catboost.load_model(model_uri)
        return model
    except Exception as e:
        raise RuntimeError(f"error loading production model: {str(e)}")


# register candidate model to mlflow registry
def register_candidate_model(candidate_run_id:str) -> dict:
    model_uri=f"runs:/{candidate_run_id}/model"
    result=mlflow.register_model(model_uri=model_uri,name=MODEL_NAME)
    return {'model_name':MODEL_NAME,'version':result.version,'run_id':result.run_id}











# from __future__ import annotations
# import shutil
# from datetime import datetime, timezone
# from catboost import CatBoostClassifier
# from app.utils.utility import (CANDIDATE_MODEL_PATH,MODEL_NAME,PRODUCTION_MODEL_PATH,REGISTRY_PATH,read_registry,write_registry,)


# def load_production_model() -> CatBoostClassifier:
#     if not PRODUCTION_MODEL_PATH.exists():
#         raise RuntimeError("No production model found. Train and register a model first.")
#     model = CatBoostClassifier()
#     model.load_model(str(PRODUCTION_MODEL_PATH))
#     return model



# def register_candidate_model(candidate_run_id: str) -> dict:
#     if not CANDIDATE_MODEL_PATH.exists():
#         raise FileNotFoundError(f"Candidate model not found: {CANDIDATE_MODEL_PATH}")

#     PRODUCTION_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
#     shutil.copy2(CANDIDATE_MODEL_PATH, PRODUCTION_MODEL_PATH)

#     registry = read_registry()
#     version = int(registry.get("version", 0)) + 1
#     payload = {
#         "model_name": MODEL_NAME,
#         "version": version,
#         "run_id": candidate_run_id,
#         "production_model_path": str(PRODUCTION_MODEL_PATH),
#         "updated_at": datetime.now(timezone.utc).isoformat(),
#     }
#     write_registry(payload)
#     return payload
