from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="cleanup_metrics_dag",
    default_args=default_args,
    description="Delete Postgres metrics older than 90 days",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["maintenance", "cleanup"],
) as dag:

    cleanup_old_metrics = PostgresOperator(
        task_id="cleanup_old_metrics",
        postgres_conn_id="postgres_default",
        sql="""
        DELETE FROM metrics
        WHERE created_at < NOW() - INTERVAL '90 days';
        """,
    )

    cleanup_old_metrics
