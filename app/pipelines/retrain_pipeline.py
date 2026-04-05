from __future__ import annotations
from app.training.train_model import train
import logging




logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__) 


def run_retraining_pipeline() -> dict:

    logger.info("starting retraining pipeline ......")
    result = train()

    if not result or "run_id" not in result:
        raise RuntimeError("Training failed to produce a valid result")
    logger.info("Retraining pipeline completed successfully", extra={"run_id": result["run_id"]})
    return result



if __name__ == "__main__":
    result = run_retraining_pipeline()
    print(result)