import os
from app.pipelines.retrain_pipeline import run_retraining_pipeline
from app.training.evaluate_model import evaluate_candidate_model
from app.mlops.mlflow_utils import register_candidate_model, promote_to_production
from pathlib import Path


# python -m initial_model

def bootstrap_first_production_model() -> dict:
    #  train
    train_result = run_retraining_pipeline()
    candidate_run_id = train_result["run_id"]

    # evaluate
    eval_result = evaluate_candidate_model(candidate_run_id)
    if not eval_result["passed"]:
        raise RuntimeError(f"Initial model failed evaluation: {eval_result['reasons']}")

    # register
    registration_result = register_candidate_model(candidate_run_id)

    # promote
    promote_to_production(version=str(registration_result["version"]))

    return {
        "train_result": train_result,
        "evaluation_result": eval_result,
        "registration_result": registration_result,
        "message": "Initial model promoted to Production successfully."
    }

if __name__ == "__main__":
    result = bootstrap_first_production_model()
    print(result)