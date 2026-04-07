


#!/bin/bash

cd "$(dirname "$0")/.."

echo "Starting PostgreSQL"
sudo service postgresql start


echo "Starting MinIO"
minio server ~/data --console-address ":9001" &

sleep 10

echo "Starting MLflow"
mlflow server \
--backend-store-uri postgresql://mlflow:mlflow1@localhost:5432/mlflowdb \
--default-artifact-root s3://mlflow \
--host 0.0.0.0 \
--port 5000