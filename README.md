# 🛡️ Fraud Detection MLOps Pipeline
Designed for scalable ML systems, reproducible experimentation, automated training pipelines, model versioning, and real-time inference.

> **Stack:** Machine Learning · FastAPI · Apache Airflow · MLflow · PostgreSQL · MinIO · Docker · Docker · Kubernetes · Streamlit 


> An end-to-end MLOps system for real-time fraud detection — featuring automated retraining, drift monitoring, experiment tracking, and a production-grade serving infrastructure.

---

## 📌 Overview

This is not just a fraud detection model. It is a **complete MLOps system** demonstrating the full machine learning lifecycle in a production-ready architecture — from data ingestion and feature engineering through real-time inference, monitoring, drift detection, and automated retraining.

| Component | Technology |
|---|---|
| Inference API | FastAPI |
| Monitoring Dashboard | Streamlit |
| Orchestration | Apache Airflow |
| Experiment Tracking | MLflow |
| Model Registry | MLflow Model Registry |
| Metadata Backend | PostgreSQL |
| Artifact Store | MinIO (S3-compatible) |
| Containerization | Docker + Docker Compose |

---

## ✅ End-to-End MLOps Pipeline

- Data ingestion pipeline
- Feature engineering
- Model training
- Model evaluation
- Automatic MLflow model registration
- Production model promotion
- Real-time prediction API
- Monitoring dashboard
- Airflow orchestration



## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        MLOps Platform                        │
│                                                             │
│   ┌───────────┐    ┌──────────────┐    ┌────────────────┐  │
│   │  FastAPI  │    │   Streamlit  │    │    Airflow     │  │
│   │Inference  │    │  Monitoring  │    │ Orchestration  │  │
│   │   API     │    │  Dashboard   │    │     DAGs       │  │
│   └─────┬─────┘    └──────┬───────┘    └───────┬────────┘  │
│         │                 │                    │            │
│   ┌─────▼─────────────────▼────────────────────▼────────┐  │
│   │                   PostgreSQL                         │  │
│   │        (Predictions + MLflow Metadata)               │  │
│   └──────────────────────┬───────────────────────────────┘  │
│                          │                                  │
│   ┌──────────────────────▼───────────────────────────────┐  │
│   │              MLflow Tracking Server                   │  │
│   │         Experiment tracking · Model Registry         │  │
│   └──────────────────────┬───────────────────────────────┘  │
│                          │                                  │
│   ┌──────────────────────▼───────────────────────────────┐  │
│   │                 MinIO (S3-compatible)                 │  │
│   │          Model artifacts · Feature stores            │  │
│   └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

- **Real-time fraud prediction** via a REST API with sub-millisecond inference
- **Automatic prediction logging** to PostgreSQL for audit trails and monitoring
- **Interactive monitoring dashboard** with Streamlit showing live model health
- **Data drift and performance monitoring** with configurable alert thresholds
- **Automated retraining pipeline** triggered by drift or performance degradation
- **Full experiment tracking** with MLflow — every run logged with metrics and parameters
- **Model registry with promotion workflow** — Staging → Production lifecycle management
- **MinIO as artifact store** — S3-compatible object storage for all model artifacts
- **PostgreSQL as MLflow backend** — production-grade metadata persistence

---

## 🔄 Main Workflows

### Bootstrap (First-Time Setup)

```
Train → Evaluate → Register → Promote to Production
```

Run once to establish your baseline model and register it to the MLflow Model Registry.

### Continuous Pipeline (Ongoing)

```
Monitor → Detect Drift → Retrain → Evaluate → Register → Promote
```

Airflow DAGs run this pipeline on a schedule. If performance or data drift exceeds thresholds, retraining is triggered automatically.

---

## 📁 Project Structure

```
fraud_detection_mlops/
├── app/
│   ├── api/                    # FastAPI REST endpoints
│   ├── dashboard/              # Streamlit monitoring dashboard
│   ├── inference/              # Model predictor and serving logic
│   ├── features/               # Feature schema and data processing
│   ├── training/               # Model training and evaluation scripts
│   ├── monitoring/             # Drift detection and performance monitoring
│   ├── mlops/                  # MLflow utilities and model registry helpers
│   ├── pipelines/              # Retraining pipeline orchestration
│   ├── airflow_dags/           # Airflow DAG definitions
│   ├── bash_operator_scripts/  # Airflow BashOperator task scripts
│   └── utils/                  # Shared utilities
│
├── data/                       # Training, test, and prediction data
├── database/                   # Local SQLite (dev) or PostgreSQL (prod)
├── mlruns/                     # MLflow local tracking (dev mode)
├── logs/                       # Application and pipeline logs
│
├── docker/
│   ├── fraud-api/              # FastAPI service Dockerfile
│   ├── fraud-dashboard/        # Streamlit dashboard Dockerfile
│   ├── fraud-airflow/          # Airflow Dockerfile + entrypoint
│   └── fraud-trainer/          # Model training Dockerfile
│
├── tests/                      # Unit and integration tests
├── docker-compose.yml          # Full stack orchestration
└── requirements.txt
....
```

---

##  Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- 8GB RAM recommended (for running all services)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/fraud-detection-mlops.git
cd fraud-detection-mlops
```

### 2. Start all services

```bash


```

This spins up: FastAPI · Streamlit · Airflow · MLflow · PostgreSQL · MinIO

### 3. Run the bootstrap pipeline

```bash
# Train and register the initial model
```

### 4. Access the services

| Service | URL | Credentials |
|---|---|---|
| Prediction API | http://localhost:8000 | — |
| API Docs (Swagger) | http://localhost:8000/docs | — |
| Monitoring Dashboard | http://localhost:8501 | — |
| MLflow UI | http://localhost:5000 | — |
| Airflow UI | http://localhost:8080 | admin / admin |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin |

---

## 🔌 API Reference

### Predict (single transaction)

```bash
POST /predict
Content-Type: application/json

{
  "transaction_id": "txn_001",
  "amount": 1500.00,
  "merchant_category": "electronics",
  "hour_of_day": 2,
  "day_of_week": 6,
  ...
}
```

**Response:**
```json
{
  "transaction_id": "txn_001",
  "is_fraud": true,
  "fraud_probability": 0.923,
  "model_version": "2",
  "prediction_id": "pred_abc123"
}
```

### Health check

```bash
GET /health
```

---

## 📊 Monitoring Dashboard

The Streamlit dashboard provides live visibility into model health and prediction activity.

**Available views:**

| View | Description |
|---|---|
| Recent predictions | Live feed of the latest scored transactions |
| High-risk transactions | Flagged transactions above the fraud threshold |
| Label updates | Ground truth feedback for model evaluation |
| Monitoring status | Current drift and performance alert state |
| Drift alert summary | Feature drift metrics with trend visualization |
| Model performance metrics | Precision, recall, F1, AUC over time |

> If no predictions have been made yet, all views will show empty state — this is expected on a fresh deployment.

---

## 🔁 Airflow DAGs

| DAG | Schedule | Description |
|---|---|---|
| `fraud_retrain_dag` | Daily / on-trigger | Full retraining pipeline: monitor → retrain → evaluate → register |
| `fraud_monitor_dag` | Hourly | Drift and performance monitoring only |

Access the Airflow UI at `http://localhost:8080` to trigger, pause, or inspect DAG runs.

---

## 📦 MLflow Experiment Tracking

Every training run logs:

- Hyperparameters and model configuration
- Evaluation metrics (AUC, F1, precision, recall)
- Feature importance plots
- Trained model artifact (stored in MinIO)
- Data statistics for drift baseline

Models are versioned and promoted through `Staging → Production` in the MLflow Model Registry.

---

## 🧪 Running Tests

```bash
# All tests
pytest tests/

# API tests only
pytest tests/test_api.py -v

# Model evaluation tests
pytest tests/test_model.py -v

# Utility tests
pytest tests/test_utility.py -v
```

---

## ⚙️ Configuration

Key environment variables (set in `docker-compose.yml` or a `.env` file):

```env
# PostgreSQL
POSTGRES_USER=fraud_user
POSTGRES_PASSWORD=fraud_pass
POSTGRES_DB=fraud_db

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_S3_ENDPOINT_URL=http://minio:9000

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET=mlflow-artifacts

# Model thresholds
FRAUD_THRESHOLD=0.5
DRIFT_THRESHOLD=0.1
PERFORMANCE_DROP_THRESHOLD=0.05
```

---

## 🧠 ML Design Decisions

**Why PostgreSQL for MLflow backend?**
SQLite is the default but not suitable for concurrent Airflow workers. PostgreSQL handles parallel writes from multiple DAG tasks without locking.

**Why MinIO for artifacts?**
MinIO is S3-compatible, so the same code works in local Docker, on-prem Kubernetes, and AWS S3 — just swap the endpoint URL.

**Why separate training and API containers?**
Decoupling training from inference means you can scale the API horizontally without carrying the training dependencies, and retrain without any API downtime.

---

## 🗺️ Roadmap

- [ ] Kubernetes deployment manifests (Helm chart)
- [ ] Feature store integration (Feast)
- [ ] Real-time streaming inference (Kafka)
- [ ] A/B model testing support
- [ ] Grafana + Prometheus observability stack
- [ ] GitHub Actions CI/CD pipeline

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙋 Author

Built as a complete MLOps reference implementation demonstrating production ML system design patterns.

> **Stack:** Machine Learning · FastAPI · Apache Airflow · MLflow · PostgreSQL · MinIO · Docker · Docker · Kubernetes · Streamlit 
