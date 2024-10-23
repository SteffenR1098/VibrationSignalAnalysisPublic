'''
    Script to create DBs and tables
'''
import sqlite3
from sqlite3 import Error

from helper_functions import get_db_parameter
from helper_db_functions import create_connection, show_tables, close_connection

# ========================================================

create_data_source_db = 0
create_AImonitor_db = 0

# ========================================================
# Get parameter for SQLite dbs and tables for data source & AImonitor
# ========================================================

source_db_file = get_db_parameter('source_db_file')
source_table_name = get_db_parameter('source_table_name')
monitor_db_file = get_db_parameter('monitor_db_file')
monitor_table_name = get_db_parameter('monitor_table_name')

# ========================================================
# Data source DB & table
# ========================================================

if create_data_source_db == 1^:

    # == Create connection to DB. If db does not yet exist it is created.
    print('-- connect to data source DB')

    db_conn = create_connection(source_db_file)

    if db_conn:

        print('-- show existing tables in DB initial')
        show_tables(db_conn)

        print('-- create table')

        sql_create_table_command = f'CREATE TABLE IF NOT EXISTS {source_table_name} ('
        sql_create_table_command += 'id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,'
        sql_create_table_command += 'classid INTEGER,'
        sql_create_table_command += 'data BLOB'
        sql_create_table_command += ');'

        print(sql_create_table_command)

        # create projects table
        try:
            c = db_conn.cursor()
            c.execute(sql_create_table_command)
            print('-- table created')
        except Error as e:
            print(e)

        print('-- show existing tables in DB end')
        show_tables(db_conn)

    print('-- close data source DB connection')
    close_connection(db_conn)

# ========================================================
# AImonitor DB & table
# ========================================================

if create_AImonitor_db == 1:

    # == Create connection to DB. If db does not yet exist it is created.
    print('-- connect to AImonitor DB')

    db_conn = create_connection(monitor_db_file)

    if db_conn:

        print('-- show existing tables in DB initial')
        show_tables(db_conn)

        print('-- create table')

        sql_create_table_command = f'CREATE TABLE IF NOT EXISTS {monitor_table_name} ('
        sql_create_table_command += 'id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,'
        sql_create_table_command += 'classid INTEGER,'
        sql_create_table_command += 'data BLOB'
        sql_create_table_command += ');'

        print(sql_create_table_command)

        # create projects table
        try:
            c = db_conn.cursor()
            c.execute(sql_create_table_command)
            print('-- table created')
        except Error as e:
            print(e)

        print('-- show existing tables in DB end')
        show_tables(db_conn)

    print('-- close AImonitor DB connection')
    close_connection(db_conn)

# ========================================================
print('-- End')
