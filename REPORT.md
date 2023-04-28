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
             JOIN stream_module t2 ON t2.id=t1.stream_module_id
             JOIN stream t3 ON t3.id=t2.stream_id
             JOIN course t4 ON t4.id=t3.course_id''',
    }
```
Далее перехожу непосредственно к Airflow-операторам.
В данном случае DAG будет состоять из одного оператора, который будет обновлять все таблицы.
