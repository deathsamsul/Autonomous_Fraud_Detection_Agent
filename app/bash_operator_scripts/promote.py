import sys
from app.mlops.mlflow_utils import promote_to_production





def main(version: str) -> None:
    promote_to_production(version)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError("version argument is required")
    main(sys.argv[1])