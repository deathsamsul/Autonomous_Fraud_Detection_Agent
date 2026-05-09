#  Autonomous Fraud Detection System with MLOps
# Production-grade real-time fraud detection platform with MLflow, Airflow, FastAPI, Kubernetes, monitoring, and automated retraining pipelines

## Overview
This project is an end-to-end MLOps-based fraud detection platform designed to detect fraudulent financial transactions in real time
The system includes:
- Real-time prediction APIs
- Automated model retraining pipelines
- Model monitoring and drift detection
- Experiment tracking and model registry
- Kubernetes-based deployment
- Observability with Prometheus and Grafana

The goal is to simulate a production-grade ML system rather than only training a machine learning model

## System Architecture
User → FastAPI → ML Model → PostgreSQL
                     ↓
              Prometheus Metrics
                     ↓
                 Grafana

Airflow DAGs
    ↓
Monitoring → Retraining → Evaluation → MLflow Registry

## Features

### Real-Time Fraud Prediction
- FastAPI inference API
- Low-latency predictions
- Probability-based fraud scoring

### MLOps Pipeline
- MLflow experiment tracking
- Model registry integration
- Automated model promotion

### Monitoring
- Data drift detection using Evidently AI
- Performance monitoring
- Prometheus metrics
- Grafana dashboards

### Automated Retraining
- Airflow DAG orchestration
- Scheduled retraining pipeline
- Candidate model evaluation

### Deployment
- Dockerized services
- Kubernetes deployment
- ConfigMaps and Secrets support

### Explainability
- SHAP-based prediction explanations

------------------------------------------------
## Tech Stack
| Category | Tools |
|---|---|
| ML | CatBoost, Scikit-learn |
| API | FastAPI |
| Dashboard | Streamlit |
| MLOps | MLflow, Airflow |
| Monitoring | Evidently AI, Prometheus, Grafana |
| Database | PostgreSQL |
| Storage | MinIO |
| Deployment | Docker, Kubernetes |
| Language | Python |


## Kubernetes Deployment
Services deployed:
- FastAPI
- PostgreSQL
- MLflow
- MinIO
- Airflow
<!-- - Prometheus
- Grafana -->
Features:
- ConfigMaps
- Secrets
- Persistent Volumes
- Namespace isolation


## Future Improvements
- Kafka streaming pipeline
- PythonToolExecutor more control and more relible
- airflow continous monitoring dag with postgresql 
- database clean up dag with 90 days old data 
- LLM-powered fraud investigation assistant


## Key Engineering Highlights

- Built a production-style ML system instead of a notebook-only project
- Designed automated retraining workflows
- Implemented real-time fraud inference APIs
- Added model monitoring and drift detection
- Containerized and orchestrated services using Kubernetes