# image built version 
from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

default_args = {
    "owner": "automated_mlops",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

PROJECT_DIR = "/opt/airflow"
APP_DIR = "/opt/airflow/app/repo/app"
PYTHON_BIN = "/opt/airflow/ml_env/bin/python"
SCRIPTS_DIR = f"{APP_DIR}/bash_operator_scripts"

# PROJECT_DIR = "/opt/airflow"
# APP_DIR = "/opt/airflow/app"
# PYTHON_BIN = "/opt/airflow/ml_env/bin/python"
# SCRIPTS_DIR = f"{APP_DIR}/bash_operator_scripts"

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
        set -euo pipefail
        cd {PROJECT_DIR}
        export PYTHONPATH=/opt/airflow/app/repo:/opt/airflow
        {PYTHON_BIN} {SCRIPTS_DIR}/monitor.py
        """,
        skip_on_exit_code=99,
    )

    retrain_task = BashOperator(
        task_id="retrain_model",
        bash_command=f"""
        set -euo pipefail
        cd {PROJECT_DIR}
        export PYTHONPATH=/opt/airflow/app/repo:/opt/airflow
        {PYTHON_BIN} {SCRIPTS_DIR}/retrain.py
        """,
        do_xcom_push=True,
    )

    evaluate_task = BashOperator(
        task_id="evaluate_model",
        bash_command=f"""
        set -euo pipefail
        cd {PROJECT_DIR}
        export PYTHONPATH=/opt/airflow/app/repo:/opt/airflow
        RUN_ID="{{{{ ti.xcom_pull(task_ids='retrain_model') }}}}"
        {PYTHON_BIN} {SCRIPTS_DIR}/evaluate.py "$RUN_ID"
        """,
        do_xcom_push=True,
    )

    register_task = BashOperator(
        task_id="register_model",
        bash_command=f"""
        set -euo pipefail
        cd {PROJECT_DIR}
        export PYTHONPATH=/opt/airflow/app/repo:/opt/airflow
        CANDIDATE_RUN_ID="{{{{ ti.xcom_pull(task_ids='evaluate_model') }}}}"
        {PYTHON_BIN} {SCRIPTS_DIR}/register.py "$CANDIDATE_RUN_ID"
        """,
        do_xcom_push=True,
    )

    promote_task = BashOperator(
        task_id="promote_model",
        bash_command=f"""
        set -euo pipefail
        cd {PROJECT_DIR}
        export PYTHONPATH=/opt/airflow/app/repo:/opt/airflow
        VERSION="{{{{ ti.xcom_pull(task_ids='register_model') }}}}"
        {PYTHON_BIN} {SCRIPTS_DIR}/promote.py "$VERSION"
        """,
    )

    monitor_task >> retrain_task >> evaluate_task >> register_task >> promote_task
