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
