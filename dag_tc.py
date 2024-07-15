from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from clickhouse_driver import Client
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 3),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "max_active_runs": 1,  # Ограничение на одновременное выполнение одного DAG
}

dag = DAG(
    "daily_sales_insert_clickhouse",
    default_args=default_args,
    description="DAG for daily insertion of 6 million rows into ClickHouse sales table",
    schedule_interval="0 23 * * *",  # каждый день 23:00
    catchup=True,  # catchup для организации бэкфилла
    max_active_tasks=1,  # Ограничение на одновременное выполнение задач в рамках DAG
)


def execute_clickhouse_query(execution_date):
    client = Client("localhost")
    query = f"""
    INSERT INTO technical_specification.sales
    SELECT 
        '{execution_date}' as execution_date,
        1000000 + rand() % 100 as article_id,
        article_id % 2 as is_pb,
        rand() % 1000 as quantity
    FROM numbers(6000000)
    """
    client.execute(query)


insert_sales_task = PythonOperator(
    task_id="insert_sales_task_clickhouse",
    python_callable=execute_clickhouse_query,
    op_kwargs={"execution_date": "{{ ds }}"},
    provide_context=True,
    dag=dag,
)

insert_sales_task
