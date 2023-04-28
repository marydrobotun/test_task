from os.path import dirname
import sys

project_path = dirname(dirname(sys.modules['__main__'].__file__))
dwh_connect_string = f'sqlite:///{project_path}/dwh.sqlite'
source_connect_string = f'sqlite:///{project_path}/database.sqlite'
