FROM apache/airflow:3.1.0-python3.11

USER root

RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc libgomp1 && rm -rf /var/lib/apt/lists/*

COPY airflow_requirements.txt /opt/airflow/airflow_requirements.txt
RUN pip install --no-cache-dir -r /opt/airflow/airflow_requirements.txt

COPY app /opt/airflow/app
COPY --chmod=755 docker/fraud-airflow/entrypoint.sh /entrypoint.sh

USER airflow

WORKDIR /opt/airflow
ENV PYTHONPATH=/opt/airflow
ENV DATA_DIR=/opt/airflow/data
ENV DB_DIR=/opt/airflow/database
ENV MODELS_DIR=/opt/airflow/models
ENV LOGS_DIR=/opt/airflow/logs
ENV MLFLOW_DIR=/opt/airflow/mlruns
ENV AIRFLOW__CORE__DAGS_FOLDER=/opt/airflow/app/airflow_dags
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:////opt/airflow/airflow.db
