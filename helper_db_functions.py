'''
    Py file for all SQLite db functionality
'''

import sqlite3
from sqlite3 import Error
import numpy as np
import io

# ======================================================

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

# ======================================================

def show_tables(db_conn):
    # Show all tables in DB
    # param: Connection object
    # return: None

    print('++ List of tables in db:')

    cursorObj = db_conn.cursor()
    cursorObj.execute('SELECT name from sqlite_master where type= "table"')
    print(cursorObj.fetchall())

    return None

# ======================================================

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

# ======================================================

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

# ======================================================

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

# ======================================================

def vacuum_db(db_conn):
    # Cleans up database and releases memory after deleting data
    # param: db_conn - Connection object
    # return: None

    print(f'++ Vacuum database:')

    #conn = sqlite3.connect('my_test.db', isolation_level=None)   #IN CASE OF PROBLEMS
    db_conn.execute("VACUUM")

    # db_conn.commit()

    return None

# ======================================================

def trans_ndarray2blob(ndarray):
    #print('++ Transform ndarray to blob')
    out = io.BytesIO()
    np.save(out, ndarray)
    out.seek(0)
    return sqlite3.Binary(out.read())

def trans_blob2ndarray(text):
    #print('++ Transform blob to ndarray')
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

# ======================================================

def insert_blob_data(db_conn, table_name, data, data_class):
    # param: Connection object
    # param: data
    # return: Cursor index

    #print(f'++ Write signals of type: {data_class} as blob to db.')
    #print(f'++ Shape of row data: {np.shape(data)}, type of {type(data)}')

    # ==== create SQL statement ====

    sql_insert_table_command = f'INSERT INTO {table_name} (classid, data) VALUES (?,?)'

    # ---------------------------------------------------

    cur = db_conn.cursor()

    # === insert data row by row
    for index in range(0, len(data)):

        #print(f'++++ Insert data set{index} in tables of DB.')

        #print('-------------------------------------------')

        #print(f'++ Shape of row data: {np.shape(data[index,:])}, type of {type(data[index,:])}')

        data_blob = trans_ndarray2blob(data[index,:])

        cur.execute(sql_insert_table_command, (data_class, data_blob))
        #db_conn.commit()

        #print(f'++++ Id of data set: {cur.lastrowid}.')

    return None

# ======================================================

def get_blob_data(db_conn, table_name, data_class):
     # param: Connection object
    # param: data_class
    # param: mode
    # return: return_list
    # return: classid_list

    #print(f'++ Read data from table {table_name}.')

    cur = db_conn.cursor()

    sql_getdata_command = f'SELECT * FROM {table_name} WHERE classid = {data_class}'

    cur.execute(sql_getdata_command)

    rows = cur.fetchall()  # returns class 'list'

    # print(f'++ Shape of row data: {np.shape(rows)}, type of {type(rows)}')
    # size_rows = np.shape(rows)
    # print(f'++ Size of rows {size_rows[0]}')

    size_rows = np.shape(rows)
    amount_of_signals = size_rows[0]
    amount_floats = 4096

    data_values = np.zeros(shape=(amount_of_signals, amount_floats))
    classid_list = []

    index = 0

    for row in rows:  

        data = row[2]
        data_convert = trans_blob2ndarray(data)

        data_values[index, :] = data_convert

        classid_list.append(row[1])

        index += 1

    #return data_values, classid_list
    data_values_32 = np.float32(data_values)
    return data_values_32

# ======================================================

def commit_data(db_conn):
    # Commit all changes to DB
    # param: db_conn - Connection object
    # return: None

    print(f'++ Commit all changes to DB.')

    db_conn.commit()

    return None

# ======================================================

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

# ======================================================
