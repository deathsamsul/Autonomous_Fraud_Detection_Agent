import mlflow
from app.utils.utility import MLFLOW_TRACKING_URI


# python -m minio_test

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("test")

with mlflow.start_run():
    mlflow.log_param("test", 1)

    with open("test.txt", "w") as f:
        f.write("hello")

    mlflow.log_artifact("test.txt")