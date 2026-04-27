import json
import sys

from app.mlops.mlflow_utils import register_candidate_model


def main(run_id: str) -> None:
    result = register_candidate_model(candidate_run_id=run_id)
    print(json.dumps(result, indent=2))
    print(str(result["version"]))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("run_id argument is required")
    main(sys.argv[1])