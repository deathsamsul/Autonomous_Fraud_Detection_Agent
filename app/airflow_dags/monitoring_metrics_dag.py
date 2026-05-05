from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score, accuracy_score
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    'monitoring_metrics_dag',
    default_args=default_args,
    description='Calculate and store model metrics for Grafana monitoring',
    schedule_interval='0 6 * * *',  # Daily at 6 AM
    catchup=False,
)


def calculate_model_metrics(**context):
    """
    Calculate model performance metrics and store in PostgreSQL.
    """
    try:
        # Load predictions and actual values (from your model output)
        # This is a placeholder - replace with your actual data source
        predictions = [0, 1, 1, 0, 1, 0, 1, 1, 0, 0]
        actual = [0, 1, 0, 0, 1, 0, 1, 0, 0, 1]
        
        # Calculate metrics
        metrics = {
            'timestamp': datetime.utcnow(),
            'accuracy': accuracy_score(actual, predictions),
            'precision': precision_score(actual, predictions, zero_division=0),
            'recall': recall_score(actual, predictions, zero_division=0),
            'f1_score': f1_score(actual, predictions, zero_division=0),
            'roc_auc': roc_auc_score(actual, predictions),
        }
        
        logger.info(f"Calculated metrics: {metrics}")
        context['task_instance'].xcom_push(key='metrics', value=metrics)
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error calculating metrics: {str(e)}")
        raise


def store_metrics_to_postgres(**context):
    """
    Store calculated metrics to PostgreSQL for Grafana visualization.
    """
    try:
        metrics = context['task_instance'].xcom_pull(
            task_ids='calculate_metrics',
            key='metrics'
        )
        
        postgres_hook = PostgresHook(postgres_conn_id='postgres_monitoring')
        
        insert_query = """
            INSERT INTO model_metrics 
            (timestamp, metric_name, metric_value, model_version)
            VALUES (%s, %s, %s, %s)
        """
        
        for metric_name, metric_value in metrics.items():
            if metric_name != 'timestamp':
                postgres_hook.run(
                    insert_query,
                    parameters=(
                        metrics['timestamp'],
                        metric_name,
                        float(metric_value),
                        'v1.0'  # Replace with actual model version
                    )
                )
        
        logger.info("Metrics stored successfully in PostgreSQL")
    
    except Exception as e:
        logger.error(f"Error storing metrics: {str(e)}")
        raise


# Create PostgreSQL table if not exists
create_metrics_table = PostgresOperator(
    task_id='create_metrics_table',
    postgres_conn_id='postgres_monitoring',
    sql="""
        CREATE TABLE IF NOT EXISTS model_metrics (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            metric_name VARCHAR(50) NOT NULL,
            metric_value FLOAT NOT NULL,
            model_version VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
        ON model_metrics(timestamp);
        
        CREATE INDEX IF NOT EXISTS idx_metrics_name 
        ON model_metrics(metric_name);
    """,
    dag=dag,
)

# Calculate metrics
calculate_metrics = PythonOperator(
    task_id='calculate_metrics',
    python_callable=calculate_model_metrics,
    provide_context=True,
    dag=dag,
)

# Store metrics to PostgreSQL
store_metrics = PythonOperator(
    task_id='store_metrics',
    python_callable=store_metrics_to_postgres,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
create_metrics_table >> calculate_metrics >> store_metrics
