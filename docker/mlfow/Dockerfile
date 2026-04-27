FROM python:3.11-slim

WORKDIR /opt/mlflow

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip first
RUN pip install --upgrade pip

COPY docker/mlfow/mlflow_requirements.txt .

RUN pip install --no-cache-dir -r mlflow_requirements.txt

COPY docker/mlfow/entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]


# docker build -f docker/mlfow/Dockerfile -t deathsamsul/mlflow:1.0 .
# docker build -t deathsamsul/mlflow:1.0 -t deathsamsul/mlflow:latest -f docker/mlfow/Dockerfile .