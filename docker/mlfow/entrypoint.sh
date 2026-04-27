#!/bin/bash  # sheband this tell the system to run this script using the bash shell

# Without set -e, the script would continue even after errors (dangerous in production).
set -e     # Exit immediately if a command exits with a non-zero status

echo "Starting MLflow server..."   # Log message to indicate the server is starting

# validate required env variables
: "${BACKEND_STORE_URI:?Need BACKEND_STORE_URI}"             # "${VAR:?message}"
: "${ARTIFACT_ROOT:?Need ARTIFACT_ROOT}"
: "${MLFLOW_S3_ENDPOINT_URL:?Need MLFLOW_S3_ENDPOINT_URL}"

mlflow server \
  --backend-store-uri "${BACKEND_STORE_URI}" \
  --default-artifact-root "${ARTIFACT_ROOT}" \
  --host 0.0.0.0 \
  --port 5000