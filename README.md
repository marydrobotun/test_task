# skyeng test_task
Это небольшое руководство о том, как запустить ETL. Отчет по тестовому заданию [здесь](https://github.com/marydrobotun/test_task/blob/main/REPORT.md) :)

Как развернуть?
1. Клонировать проект

```git clone https://github.com/marydrobotun/test_task.git```

2. Установить Airflow, как описано в [документации](https://airflow.apache.org/docs/apache-airflow/stable/start.html)

3. Установить зависимости. Находясь в папке проекта, выполнить команду:

```pip install requirements.txt```

4. В файле airflow.cfg поменять dags_folder на путь к папке [dags](https://github.com/marydrobotun/test_task/tree/main/dags) внутри проекта. Например:

```dags_folder = ~/my_projects/skyeng_test/dags```

5. В файле [common/settings.py](https://github.com/marydrobotun/test_task/blob/main/common/settings.py) указать подключения к базам данных

6. Добавить папку [common](https://github.com/marydrobotun/test_task/tree/main/common) в переменную PYTHONPATH. Например:

```export PYTHONPATH="$PYTHONPATH:~/my_projects/skyeng_test/common"```

7. Запустить Airflow в тестовом режиме

```airflow standalone```

8. Зайти на localhost:8080 и увидеть там наш даг:

![source](https://github.com/marydrobotun/test_task/blob/main/docs/airflow.png)

