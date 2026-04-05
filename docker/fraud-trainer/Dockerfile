FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY app /app/app
ENV PYTHONPATH=/app
ENV DATA_DIR=/app/data
ENV DB_DIR=/app/database
ENV MODELS_DIR=/app/models
ENV LOGS_DIR=/app/logs
ENV MLFLOW_DIR=/app/mlruns
CMD ["python", "-m", "app.pipelines.retrain_pipeline"]
