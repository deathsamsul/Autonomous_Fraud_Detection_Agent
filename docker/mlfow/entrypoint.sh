#!/bin/bash

set -e

echo "Starting MLflow server..."

: "${BACKEND_STORE_URI:?Need BACKEND_STORE_URI}"
: "${ARTIFACT_ROOT:?Need ARTIFACT_ROOT}"
: "${MLFLOW_S3_ENDPOINT_URL:?Need MLFLOW_S3_ENDPOINT_URL}"

mlflow server \
  --backend-store-uri "${BACKEND_STORE_URI}" \
  --default-artifact-root "${ARTIFACT_ROOT}" \
  --host 0.0.0.0 \
  --port 5000