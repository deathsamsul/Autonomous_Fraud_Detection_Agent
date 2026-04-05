# Fraud Detection MLOps

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_sample_data.py
python -m app.training.train_model
python -c "from app.mlops.mlflow_utils import register_candidate_model; print(register_candidate_model('manual-local'))"
uvicorn app.api.api:app --reload
```

## Docker

```bash
python scripts/generate_sample_data.py
docker compose build
docker compose --profile trainer up fraud-trainer
docker compose up
```
