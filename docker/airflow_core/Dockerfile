FROM apache/airflow:3.2.0-python3.11

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --chown=airflow:airflow airflow_requirements.txt /tmp/airflow_requirements.txt

USER airflow

RUN python -m pip install --no-cache-dir -r /tmp/airflow_requirements.txt && \
    rm -f /tmp/airflow_requirements.txt

ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONPATH=/opt/airflow:/opt/airflow/app

WORKDIR /opt/airflow