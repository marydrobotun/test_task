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
