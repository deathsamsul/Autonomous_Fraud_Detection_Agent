from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator




default_args = { "owner": "automated_mlops",
                "depends_on_past": False,"retries": 1,
                "retry_delay": timedelta(minutes=5),}



PROJECT_DIR = "/opt/airflow"
PYTHON_BIN = "python"
SCRIPTS_DIR = f"{PROJECT_DIR}/app/bash_operator_scripts"

with DAG(
    dag_id="fraud_retrain_4step_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="@weekly",
    catchup=False,
    max_active_runs=1,
    tags=["fraud", "mlops", "airflow"],
) as dag:
    monitor_task = BashOperator(
        task_id="monitor_model",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        export PYTHONPATH={PROJECT_DIR}
        {PYTHON_BIN} {SCRIPTS_DIR}/monitor.py
        """,
        skip_on_exit_code=99,
    )

    retrain_task = BashOperator(
        task_id="retrain_model",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        export PYTHONPATH={PROJECT_DIR}
        {PYTHON_BIN} {SCRIPTS_DIR}/retrain.py > /tmp/retrain_{{{{ run_id }}}}.json
        """,
    )

    evaluate_task = BashOperator(
        task_id="evaluate_model",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        export PYTHONPATH={PROJECT_DIR}
        RUN_ID=$({PYTHON_BIN} -c "import json; print(json.load(open('/tmp/retrain_{{{{ run_id }}}}.json'))['run_id'])")
        {PYTHON_BIN} {SCRIPTS_DIR}/evaluate.py "$RUN_ID" > /tmp/eval_{{{{ run_id }}}}.json
        """,
    )

    register_task = BashOperator(
        task_id="register_model",
        bash_command=f"""
        set -e
        cd {PROJECT_DIR}
        export PYTHONPATH={PROJECT_DIR}
        RUN_ID=$({PYTHON_BIN} -c "import json; print(json.load(open('/tmp/eval_{{{{ run_id }}}}.json'))['candidate_run_id'])")
        {PYTHON_BIN} {SCRIPTS_DIR}/register.py "$RUN_ID"
        """,
    )

    monitor_task >> retrain_task >> evaluate_task >> register_task
