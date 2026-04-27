FROM apache/airflow:3.2.0-python3.11

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-venv \
    build-essential \
    git \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow
# ENV PYTHONUNBUFFERED=1 # Ensure that Python output is sent straight away without buffering

COPY --chown=airflow:airflow airflow_requirements.txt /tmp/airflow_requirements.txt
RUN python -m pip install --no-cache-dir -r /tmp/airflow_requirements.txt && \
    rm -f /tmp/airflow_requirements.txt

RUN python -m venv /opt/airflow/ml_env

COPY --chown=airflow:airflow requirements.txt /tmp/requirements.txt
RUN /opt/airflow/ml_env/bin/python -m pip install --no-cache-dir --upgrade pip && \
    /opt/airflow/ml_env/bin/python -m pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm -f /tmp/requirements.txt

ENV AIRFLOW_HOME=/opt/airflow
ENV PYTHONPATH=/opt/airflow:/opt/airflow/app

WORKDIR /opt/airflow