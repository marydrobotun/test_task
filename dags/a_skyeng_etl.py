from os.path import dirname
import sys
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from utils import save_data_to_table
from settings import source_connect_string, dwh_connect_string
from entities import entities


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 4, 28)
}
dag = DAG('etl_process', default_args=default_args, schedule_interval="@hourly")


def etl():
    """This is the main ETL function."""
    source_engine = create_engine(source_connect_string)
    for table in entities:
        table_data = pd.read_sql(table['query_to_get_data'], source_engine)
        save_data_to_table(table_data, table, dwh_connect_string)


etl_operator = PythonOperator(
    task_id='load_data',
    python_callable=etl,
    dag=dag
)
etl_operator
