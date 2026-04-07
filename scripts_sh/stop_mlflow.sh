#!/bin/bash

cd "$(dirname "$0")/.."

echo "Stopping MLflow..."

pkill -f mlflow

echo "Stopping MinIO..."

pkill -f minio

echo "Stopped all services"