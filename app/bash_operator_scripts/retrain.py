import json
from app.pipelines.retrain_pipeline import run_retraining_pipeline






def main() -> None:

    result = run_retraining_pipeline()

    if result is None or "run_id" not in result:
        raise RuntimeError("Invalid retrain result")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
