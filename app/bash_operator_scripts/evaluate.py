import json
import sys

from app.training.evaluate_model import evaluate_candidate_model


def main(run_id: str) -> None:
    result = evaluate_candidate_model(candidate_run_id=run_id)
    if not result.get("passed", False):
        raise RuntimeError(f"Evaluation failed: {result.get('reasons', [])}")
    print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1])
