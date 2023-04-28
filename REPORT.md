# Отчет по заданию
## 1-2. Схема данных в DWH
Изначально данные в БД-источнике находятся в 3NF:
![source](https://github.com/marydrobotun/test_task/blob/master/docs/3nf.png)

В данном случае, так как целью задачи является витрина данных для анализа и визуализации, я считаю целесообразным выбрать схему “Звезда”. Данная схема очень проста, дает большую производительность, и является стандартом для витрин данных. Многие BI инструменты хорошо работают с такими схемами. Недостаток данной схемы - относительно высокий уровень избыточности данных, однако он компенсируется повышением производительности. Также, если мы предполагаем, что уже загруженные строки не будут обновляться, эта избыточность данных не дает возможность для появления аномалий.
Таким образом, схема модели в хранилище:
![source](https://github.com/marydrobotun/test_task/blob/master/docs/star.png)
## 3. ETL
Здесь я выделила два случая.
1. У нас в таблицах БД-источника появились новые данные. То есть, в таблицах БД-источника появились id, которые отсутствуют в БД-хранилище. В этом случае нам нужно дозаписать все новые строки в БД-хранилище.
2. В таблицах БД-источника произошли изменения некоторых строк, которые уже ранне были загружены в хранилище. Из контекста я поняла, что колонка updated_at как раз показывает, когда в последний раз была изменена та или иная строка. В этом случае нам нужно сравнить updated_at в источнике и хранилище и при необходимости обновить данные в БД-хранилище.

В качестве инструмента ETL я выбираю Airflow. Тестовые БД - SQLite, для работы с данными - pandas, для подключения к БД - SQLAlchemy.
Для начала создаю вспомогательную функцию, которая будет сохранять в БД данные из pandas DataFrame. Данная функция принимает DataFrame, словарь с атрибутами таблицы (название и первичный ключ) и строку коннекта к БД. Функция проверяет, есть ли уже в БД такая таблица. Если есть, то все строки, которые в ней уже есть, удаляются из датафрейма (сравнение по первичному ключу), чтобы записывались только новые строки. Также она проверяет поле updated_at, если в таблице БД устаревшие данные, она их обновляет. (Здесь я использовала DELETE + INSERT вместо UPDATE из-за простоты, однако для улучшения производительности в реальном проекте лучше сделать замену на UPDATE)

```python
import pandas as pd
from sqlalchemy import create_engine, inspect


def save_data_to_table(data, table, connection_string):
    """ This function gets:
       data: pandas DataFrame with data that should be loaded
       table: dict with data about table: should contain table_name and primary_key
       connection_string: str, contains connection to a database
       This function checks whether the table already exists in a database, and if so,
       deletes all the data which is already loaded to the table out of the dataframe
       After that, it saves all the new data to the table provided in the arguments
       If there is an "updated_at" column, it also checks whether the value of it in
       new dataframe is bigger, and if so, updates it in a database

    """
    engine = create_engine(connection_string)
    table_name = table['table_name']
    pk = table['pk']

    if inspect(engine).has_table(table_name):
        if 'updated_at' in data.columns:
            old_data = pd.read_sql(f'select id, updated_at from {table_name}', engine)
            data_to_update = data.merge(old_data, on='id', how='left')
            data_to_update = data_to_update[data_to_update['updated_at_x'] > data_to_update['updated_at_y']]
            data_to_update.drop(['updated_at_y'], axis=1, inplace=True)
            data_to_update.rename(columns={'updated_at_x': 'updated_at'}, inplace=True)

            for index, row in data_to_update.iterrows():
                id = row['id']
                delete_sql = f'DELETE FROM {table_name} WHERE id={id}'
                engine.execute(delete_sql)
            data_to_update.to_sql(table_name, con=engine, index=False, if_exists='append')

        old_data = pd.read_sql(f'select id from {table_name}', engine)
        data = data[~data[pk].isin(old_data[pk])]

    data.to_sql(table_name, con=engine, index=False, if_exists='append')

```

Также я создаю отдельный файл, в котором будут лежать данные о сущностях. Всего у нас 4 сущности: урок, модуль, поток, курс. В терминологии методологии "звезда" урок является таблицей фактов, остальные - таблицами измерений. По каждой сущности я сохраняю следующие данные:
1. имя сущности
2. имя таблицы, которая относится к данной сущности
3. первичный ключ таблицы
4. sql-запрос для получения из источника данных по сущности
Пример для таблицы фактов:
```python
{

        'entity_name': 'lesson',
        'table_name': 'stream_module_lesson',
        'pk': 'id',
        'query_to_get_data': '''SELECT t1.*, t2.id as stream_module_id,
             t3.id as stream_id, t4.id as course_id
             FROM stream_module_lesson t1
             LEFT JOIN stream_module t2 ON t2.id=t1.stream_module_id
             LEFT JOIN stream t3 ON t3.id=t2.stream_id
             LEFT JOIN course t4 ON t4.id=t3.course_id''',
}
```
Далее перехожу непосредственно к Airflow-операторам.
В данном случае DAG будет состоять из одного оператора, который будет обновлять все таблицы. Запуск будет производиться по расписанию каждый час.
```python
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
```
Таким образом DAG выглядит на UI Airflow:
![source](https://github.com/marydrobotun/test_task/blob/master/docs/dag.png)

Как видно из этого скриншота, он работает по расписанию, как и предполагалось:

![source](https://github.com/marydrobotun/test_task/blob/master/docs/dag_history.png)

## 4. Витрина данных
