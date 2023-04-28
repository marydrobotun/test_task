# Отчет по заданию
## 1-2. Схема данных в DWH
Изначально данные в БД-источнике находятся в 3NF:
![source](https://github.com/marydrobotun/test_task/blob/master/docs/3nf.png)

В данном случае, так как целью задачи является витрина данных для анализа и визуализации, я считаю целесообразным выбрать схему “Звезда”. Данная схема очень проста, дает большую производительность, и является стандартом для витрин данных. Многие BI инструменты хорошо работают с такими схемами. Недостаток данной схемы - относительно высокий уровень избыточности данных, однако он компенсируется повышением производительности. Также, если мы предполагаем, что уже загруженные строки не будут обновляться, эта избыточность данных не дает возможность для появления аномалий.
Таким образом, схема модели в хранилище:
![source](https://github.com/marydrobotun/test_task/blob/master/docs/star.png)
## 3. ETL
В качестве инструмента ETL я выбираю Airflow. Тестовые БД - SQLite, для работы с данными - pandas, в качестве ORM - SQLAlchemy.
Для начала создаю вспомогательную функцию, которая будет сохранять в БД данные из pandas DataFrame. Данная функция принимает DataFrame, словарь с атрибутами таблицы (название и первичный ключ) и строку коннекта к БД. Функция проверяет, есть ли уже в БД такая таблица. Если есть, то все строки, которые в ней уже есть, удаляются из датафрейма (сравнение по первичному ключу), чтобы записывались только новые строки.
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
    """
    engine = create_engine(connection_string)
    table_name = table['table_name']
    pk = table['pk']
    if inspect(engine).has_table(table_name):
        old_data = pd.read_sql(f'select id from {table_name}', engine)
        data = data[~data[pk].isin(old_data[pk])]
    data.to_sql(table_name, con=engine, index=False, if_exists='append')
```
