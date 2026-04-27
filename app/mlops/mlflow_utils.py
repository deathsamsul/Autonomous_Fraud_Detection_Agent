from app.utils.utility import MLFLOW_TRACKING_URI, MODEL_NAME
from catboost import CatBoostClassifier
import mlflow.catboost



# initial pipeline
# train → evaluate → register → promote to production

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




def promote_to_production(version: str, stage: str = "Production"):

    client = mlflow.MlflowClient()
    client.transition_model_version_stage(name=MODEL_NAME,version=version,stage=stage)
    print(f"Model {MODEL_NAME} version {version} moved to {stage}.")



def archive_current_production():
    
    client = mlflow.MlflowClient()
    prod_versions = client.get_latest_versions(MODEL_NAME, stages=["Production"])
    for v in prod_versions:
        client.transition_model_version_stage(
            name=MODEL_NAME,
            version=v.version,
            stage="Archived"
        )
        print(f"Archived version {v.version}")