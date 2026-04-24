import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.training.evaluate_model import evaluate_candidate_model


def main(run_id: str) -> None:
    result = evaluate_candidate_model(candidate_run_id=run_id)
    print("Evaluation result:")
    print(json.dumps(result, indent=2))
    if not result.get("passed", False):
        # raise RuntimeError(f"Evaluation failed: {result.get('reasons', [])}")
        sys.exit(1)
    
    print(json.dumps(result))


if __name__ == "__main__":
    main(sys.argv[1])
