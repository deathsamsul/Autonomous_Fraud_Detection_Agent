import json
import sys

from app.monitoring.monitoring import run_monitoring_pipeline


def main() -> None:
    result = run_monitoring_pipeline()   # poor model performance  True
    if not result:
        print(json.dumps({"should_retrain": False, "message": "No retraining needed"}))
        sys.exit(99)
    print(json.dumps({"should_retrain": True}))


if __name__ == "__main__":
    main()
