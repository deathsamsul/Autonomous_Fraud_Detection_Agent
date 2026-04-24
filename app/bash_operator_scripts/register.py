import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from app.mlops.mlflow_utils import register_candidate_model




def main(run_id: str) -> None:
    result = register_candidate_model(candidate_run_id=run_id)
    print(json.dumps(result))

if __name__ == "__main__":
    main(sys.argv[1])



