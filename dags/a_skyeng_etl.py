import sqlite3
import pandas as pd
from sqlalchemy import create_engine, inspect
from datetime import datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from utils import save_data_to_table
from settings import source_connect_string, dwh_connect_string
from entities import entities


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022, 1, 1)
}
dag = DAG('etl_process', default_args=default_args, schedule_interval=None)
# оператор для чтения данных из table1 и записи их во временный файл


# функция для чтения данных из временного файла и записи их в table2
def etl():
    source_engine = create_engine(source_connect_string)
    for table in entities:
        table_data = pd.read_sql(table['query_to_get_data'], source_engine)
        save_data_to_table(table_data, table, dwh_connect_string)

# оператор для записи данных из временного файла в table2
t1 = PythonOperator(
    task_id='load_data',
    python_callable=etl,
    dag=dag
)
# установка зависимостей между задачами
t1
