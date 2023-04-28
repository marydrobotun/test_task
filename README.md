# test_task
skyeng test task
Как развернуть?
1. Клонировать проект
```git clone https://github.com/marydrobotun/test_task.git```
2. Установить Airflow, как описано в документации
3. В файле airflow.cfg поменять dags_folder на путь к папке dags внутри проекта. Например:
```dags_folder = ~/my_projects/skyeng_test/dags```
3. Выполнить команду:
```export PYTHONPATH="$PYTHONPATH:~/my_projects/skyeng_test/common"```
4. Запустить Airflow в тестовом режиме
```airflow standalone```
