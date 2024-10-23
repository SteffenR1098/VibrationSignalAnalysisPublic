'''
    Py file for all SQLite db functionality
'''

import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    # Create connection to DB
    # param db_file: database file
    # return: Connection object or None

    db_conn = None
    try:
        db_conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    print(f'++ Connected to {db_file}.')

    return db_conn


def show_tables(db_conn):
    # Show all tables in DB
    # param: Connection object
    # return: None

    print('++ List of tables in db:')

    cursorObj = db_conn.cursor()
    cursorObj.execute('SELECT name from sqlite_master where type= "table"')
    print(cursorObj.fetchall())

    return None


def show_data(db_conn, table):
    # Show all data of table
    # param: db_conn - Connection object
    # param: table - table name
    # return: None

    print(f'++ Show all data in table {table}:')

    cur = db_conn.cursor()
    cur.execute(f'SELECT * FROM {table}')

    rows = cur.fetchall()

    for row in rows:
        print(row)

    return None


def show_some_data(db_conn, table):
    # Show data of first 10 rows of table
    # param: db_conn - Connection object
    # param: table - table name
    # return: None

    print(f'++ Show data from first 10 rows in table {table}:')

    cur = db_conn.cursor()
    # cur.execute(f'SELECT TOP 10 * FROM {table}')
    cur.execute(f'SELECT * FROM {table} LIMIT 10')

    rows = cur.fetchall()

    for row in rows:
        print(row)

    return None


def delete_data(db_conn, table):
    # Delete all rows in table
    # param: db_conn - Connection object
    # param: table - table name
    # return: None

    print(f'++ Delete all data from table {table}:')

    sql = f'DELETE FROM {table}'
    cur = db_conn.cursor()
    cur.execute(sql)
    # db_conn.commit()

    return None

def vacuum_db(db_conn):
    # Cleans up database and releases memory after deleting data
    # param: db_conn - Connection object
    # return: None

    print(f'++ Vacuum database:')

    #conn = sqlite3.connect('my_test.db', isolation_level=None)   #IN CASE OF PROBLEMS
    db_conn.execute("VACUUM")

    # db_conn.commit()

    return None


def commit_data(db_conn):
    # Commit all changes to DB
    # param: db_conn - Connection object
    # return: None

    print(f'++ Commit all changes to DB.')

    db_conn.commit()

    return None


def close_connection(db_conn):
    # param: db_conn - Connection object
    # return: None

    try:
        if db_conn:
            db_conn.close()
        else:
            print('++ No Connection object.')
    except Error as e:
        print(e)
    finally:
        print(f'++ Connection closed.')

    return None
