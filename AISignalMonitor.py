'''
    Core class AI Signal Monitor to collect data, train AI model and classify in operational mode.
    The Signal Monitor can be connected to a real life vibration sensor with FFT modul or to a "simulated" data source.
'''

# ========================================================
# imports

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from joblib import dump, load
import sqlite3
from sqlite3 import Error
from os import path
import time

# ========================================================
# own imports of functions that are used often and 
# to provide central file to store all relevant parameters

from helper_db_functions import trans_ndarray2blob, trans_blob2ndarray, state_is_UTF8, create_connection, close_connection
from helper_functions import get_AI_parameter, get_parameter

# ========================================================

class AISignalMonitor():
    '''
        class to simulate data source. A vibration sensor and FFT module would provide data in a similar way
        methods: __init__: class constructor. Initialization including loading all data from the data source SQLite DB 
                 __del__: class descructor
                 onSignal: iteration of recieving data from data source
                 onStateChange: change state of AI Signal monitor for different functionality
    '''

    def __init__(self, state, dbPath, tablename, modelPath, logger):
        '''
            class constructor: 
            - setting initial state, variables, indices an counters
            - clear db of old data
            - initialize AI model
        '''

        # setting variables
        self.dbPath = dbPath
        self.tablename = tablename
        self.modelPath = modelPath
        self.logger = logger

        self.ratio_test_train = get_AI_parameter('test_train_split')

        self.logger.print('AIMon! Initialize.')

        self.allowed_states = ['collecting_good', 'collecting_bad', 'collecting_additional', 'check_stored_data', 'train', 'save_model', 'load_model', 'evaluate', 'purge_db', 'purge_db_good', 'purge_db_bad', 'purge_db_add']

        if state in self.allowed_states:
            self.state = state
            self.logger.stateChange('AIMon! Initial state set: ' + state + '.')
        else:
            self.state = self.states[0]
            self.logger.stateChange('AIMon! WARNING Initial state not valid. Set to default.')

        self.counter = 0
        self.show_progress = 0

        self.model_trained = 0

        # --------------------------------------------------------
        # Clear db table
        # --------------------------------------------------------

        self.logger.print('AIMon! Create DB connection.')

        self.db_conn = create_connection(self.dbPath)

        if self.db_conn:

            try:
                c = self.db_conn.cursor()
            except Error as e:
                self.logger.print(f'Error when creating cursor to db')


            #clear table of old values

            deleteTableStatement = f'DELETE FROM {self.tablename}'

            try:
                c.execute(deleteTableStatement)
                self.db_conn.commit()
                self.logger.print('AIMon! Table cleared.')
            except Error as e:
                self.logger.print('AIMon! ERROR while deleting stored data!')

            # also use vacuum to control size of SQLite db
            try:
                self.db_conn.execute('vacuum')
                self.db_conn.commit()
                self.logger.print('AIMon! DB "vacuum" completed.')
            except Error as e:
                self.logger.print('AIMon! ERROR while "vacuum" db.')

        else:
            self.logger.print('Error: No Connection to db.')

        # --------------------------------------------------------
        # initialize ML model
        # --------------------------------------------------------

        self.logger.print('AIMon! Start AI model.')

        self.model = DecisionTreeClassifier()

        close_connection(self.db_conn)

        self.logger.print('AIMon! Initialize completed.')

    # ========================================================
    # ========================================================

    def __del__(self):
        '''
            Class destructor
        '''
        self.logger.print('AIMon! End.')

    # ========================================================
    # ========================================================

    def onSignal(self, signal):
        '''
            Method to recieve new data signal. Depending on the state of the Signal Monitor, a different action is taken.
            Functionality and general messaging are separated in two different state evaluation parts  (to avoid redundance in messaging with exception of messages for evaluation).
            
        '''
        signal_is_empty = (signal is None)

        # -------------------------------------------------------

        if not signal_is_empty:
            if not np.isfinite(signal).all():
                if self.state == 'evaluate':
                    self.logger.printEval('AIMon! ERROR - INVALID signal!')
                else:
                    self.logger.print('AIMon! ERROR!!! onSignal - signal is INVALID ERROR!!!.')
                return None

        # -------------------------------------------------------
        
        self.db_conn = create_connection(self.dbPath)

        # --------------------------------------------------------
        # Messaging
        # --------------------------------------------------------

        if self.state in ['collecting_good', 'collecting_bad', 'collecting_additional']: 

            if self.counter >= 49:
                if signal_is_empty:
                    if self.show_progress == 0:
                        self.logger.print(f'AIMon! onSignal ({self.state}). Empty signal - 50.')
                        self.show_progress = 1
                    else:
                        self.logger.print(f'AIMon! onSignal ({self.state}). Empty signal - 50 x.')
                        self.show_progress = 0
                else:
                    if self.show_progress == 0:
                        self.logger.print(f'AIMon! onSignal ({self.state}) - 50.')
                        self.show_progress = 1
                    else:
                        self.logger.print(f'AIMon! onSignal ({self.state}) - 50 x.')
                        self.show_progress = 0
                self.counter = 0
            else:
                self.counter += 1

        # --------------------------------------------------------
        elif self.state in ['check_stored_data', 'save_model', 'load_model', 'train', 'purge_db', 'purge_db_good', 'purge_db_bad', 'purge_db_add', 'evaluate']:

            if self.counter >= 49:
                if self.show_progress == 0:
                    self.logger.print(f'AIMon! onSignal ({self.state}) - 50.')
                    self.show_progress = 1
                else:
                    self.logger.print(f'AIMon! onSignal ({self.state}) - 50 x.')
                    self.show_progress = 0
                self.counter = 0
            else:
                self.counter += 1

        # --------------------------------------------------------
        # Functionality
        # --------------------------------------------------------

        if self.state in ['collecting_good', 'collecting_bad', 'collecting_additional']: 

            # store labeled signal in db
            
            if self.state == 'collecting_good':
                data_class = 0
            elif self.state == 'collecting_bad':
                data_class = 1
            elif self.state == 'collecting_additional':
                data_class = 2

            if not signal_is_empty:
                if self.db_conn:

                    # == create SQL statement
                    sql_insert_table_command = f'INSERT INTO {self.tablename} (classid, data) VALUES (?,?)'

                    try:
                        cur = self.db_conn.cursor()
                    except:
                        self.logger.print('AIMon! ERROR. when accessing cursor to db!')

                    if signal.ndim == 1:

                        # === insert single signal
                        try:
                            data_blob = trans_ndarray2blob(signal)
                            cur.execute(sql_insert_table_command, (data_class, data_blob))
                        except Error as e:
                            self.logger.print(f'AIMon! ERROR. No insert in DB ({self.state}).')

                    elif signal.ndim == 2:

                        # === insert data row by row
                        for index in range(0, len(signal)):

                            try:
                                data_blob = trans_ndarray2blob(signal[index,:])
                                cur.execute(sql_insert_table_command, (data_class, data_blob))
                            except Error as e:
                                self.logger.print(f'AIMon! ERROR. No insert in DB ({self.state}).')

                    self.db_conn.commit()
                else:
                    self.logger.print(f'AIMon! ERROR no DB connection ({self.state}).')
   
        # --------------------------------------------------------
        elif self.state == 'evaluate':

            if self.model_trained == 0:
                #self.logger.print('AIMon! ERROR onSignal (evaluate) - AI model not trained ERROR.')
                self.logger.printEval('AIMon! ERROR: AI model not trained!')
                return

            if signal_is_empty:
                self.logger.printEval('AIMon! evaluate: Empty data signal.')
            else:
                amount_floats = get_parameter('signal_length')

                signal_array = np.zeros(shape=(1, amount_floats), dtype=np.float32)

                signal_array[0,:] = signal

                # -- test signal data
                prediction = self.model.predict(signal_array)

                if prediction == 0:
                    self.logger.printEval('AIMon! evaluate: Good signal!')
                elif prediction == 1:
                    self.logger.printEval('AIMon! evaluate: Bad signal!')
                elif prediction == 2:
                    self.logger.printEval('AIMon! evaluate: Additional signal!')
                else:
                    self.logger.printEval('AIMon! evaluate: ERROR: No prediction!')
                    
        # --------------------------------------------------------
        close_connection(self.db_conn)

    # ========================================================
    # ========================================================

    def onStateChange(self, state):
        '''
            Method to change state of class
            Includes functionality to check stored data, training the ML model and deleting collected data from DB
        '''

        # == open db connection
        self.db_conn = create_connection(self.dbPath)

        self.logger.stateChange('AIMon! Changing state.')

        if state_is_UTF8(state):
            state_new = state.decode('utf-8')
        else:
            state_new = state

        if state_new in self.allowed_states:
            self.state = state_new
            self.logger.stateChange('AIMon! State changed: ' + state_new)
        else:
            self.logger.stateChange('AIMon! WARNING New state not valid:' + state_new)

        # --------------------------------------------------------
        if self.state == 'check_stored_data':

            self.logger.print('AIMon! Check stored data.')

            data_class = 0
            sql_countgooddata_command = f'SELECT COUNT(*) FROM {self.tablename} WHERE classid = {data_class}'

            data_class = 1
            sql_countbaddata_command = f'SELECT COUNT(*) FROM {self.tablename} WHERE classid = {data_class}'

            data_class = 2
            sql_countadddata_command = f'SELECT COUNT(*) FROM {self.tablename} WHERE classid = {data_class}'

            try:
                cur = self.db_conn.cursor()

                cur.execute(sql_countgooddata_command)
                result_good = cur.fetchall()

                cur.execute(sql_countbaddata_command)
                result_bad = cur.fetchall()

                cur.execute(sql_countadddata_command)
                result_add = cur.fetchall()

            except Error:
                self.logger.print('AIMon! ERROR when counting data sets.')

            amount_good = (result_good[0])[0]
            amount_bad= (result_bad[0])[0]
            amount_add= (result_add[0])[0]

            amount_total = amount_good + amount_bad + amount_add

            if amount_total == 0:
                self.logger.print('AIMon! no data stored.')
            else:
                self.logger.print('AIMon! Total amount: ' + str(amount_total) + ' good: ' + str(amount_good) + ' bad: ' + str(amount_bad) + ' additional: ' + str(amount_add) + '.')

        # --------------------------------------------------------
        elif self.state == 'train':

            self.logger.stateChange('AIMon! train.')

            # -- get data from db
            # ........................................................

            time_01 = time.time()

            if self.db_conn:

                # --- get data ---
                data_class = 0
                sql_getdatagood_command = f'SELECT * FROM {self.tablename} WHERE classid = {data_class}'

                data_class = 1
                sql_getdatabad_command = f'SELECT * FROM {self.tablename} WHERE classid = {data_class}'

                data_class = 2
                sql_getdataadd_command = f'SELECT * FROM {self.tablename} WHERE classid = {data_class}'

                amount_floats = 4096

                try:
                    cur = self.db_conn.cursor()

                    cur.execute(sql_getdatagood_command)
                    rows_good = cur.fetchall()  

                    cur.execute(sql_getdatabad_command)
                    rows_bad = cur.fetchall()  

                    cur.execute(sql_getdataadd_command)
                    rows_add = cur.fetchall()  

                except Error:
                    self.logger.print('AIMon! ERROR when getting data from db.')

                # --- good data ---

                amount_of_signals_good = len(rows_good)
                data_good = np.zeros(shape=(amount_of_signals_good, amount_floats), dtype=np.float32)

                index = 0

                for row_good in rows_good:

                    data = row_good[4]
                    data_good[index, :] = trans_blob2ndarray(data)

                    index += 1

                # --- bad data ---
                amount_of_signals_bad = len(rows_bad)

                data_bad = np.zeros(shape=(amount_of_signals_bad, amount_floats), dtype=np.float32)

                index = 0

                for row_bad in rows_bad:

                    data = row_bad[4]
                    data_bad[index, :] = trans_blob2ndarray(data)

                    index += 1

                # --- add data ---
                amount_of_signals_add = len(rows_add)

                data_add = np.zeros(shape=(amount_of_signals_add, amount_floats), dtype=np.float32)

                index = 0

                for row_add in rows_add:

                    data = row_add[4]
                    data_add[index, :] = trans_blob2ndarray(data)

                    index += 1

            # -- prepare train and test data
            # ........................................................

            if amount_of_signals_good > 0:
                result_good = np.zeros(shape=(amount_of_signals_good, 1), dtype=np.float32)
                X_Train_Good, X_Test_Good, y_train_good, y_test_good = train_test_split(data_good, result_good, test_size=self.ratio_test_train)

            if amount_of_signals_bad > 0:
                result_bad = np.zeros(shape=(amount_of_signals_bad, 1), dtype=np.float32)+1
                X_Train_Bad, X_Test_Bad, y_train_bad, y_test_bad = train_test_split(data_bad, result_bad, test_size=self.ratio_test_train)

            if amount_of_signals_add > 0:
                result_add = np.zeros(shape=(amount_of_signals_add, 1), dtype=np.float32)+2
                X_Train_Add, X_Test_Add, y_train_add, y_test_add = train_test_split(data_add, result_add, test_size=self.ratio_test_train)

            if amount_of_signals_good > 0 and amount_of_signals_bad > 0 and amount_of_signals_add == 0:
                X_Train = np.concatenate((X_Train_Good, X_Train_Bad), axis=0)
                X_Test = np.concatenate((X_Test_Good, X_Test_Bad), axis=0)
                y_train = np.concatenate((y_train_good, y_train_bad), axis=0)
                y_test = np.concatenate((y_test_good, y_test_bad), axis=0)
            elif amount_of_signals_good > 0 and amount_of_signals_bad == 0 and amount_of_signals_add > 0:
                X_Train = np.concatenate((X_Train_Good, X_Train_Add), axis=0)
                X_Test = np.concatenate((X_Test_Good, X_Test_Add), axis=0)
                y_train = np.concatenate((y_train_good, y_train_add), axis=0)
                y_test = np.concatenate((y_test_good, y_test_add), axis=0)
            elif amount_of_signals_good == 0 and amount_of_signals_bad > 0 and amount_of_signals_add > 0:
                X_Train = np.concatenate((X_Train_Bad, X_Train_Add), axis=0)
                X_Test = np.concatenate((X_Test_Bad, X_Test_Add), axis=0)
                y_train = np.concatenate((y_train_bad, y_train_add), axis=0)
                y_test = np.concatenate((y_test_bad, y_test_add), axis=0)
            elif amount_of_signals_good > 0 and amount_of_signals_bad > 0 and amount_of_signals_add > 0:
                X_Train = np.concatenate((X_Train_Good, X_Train_Bad, X_Train_Add), axis=0)
                X_Test = np.concatenate((X_Test_Good, X_Test_Bad, X_Test_Add), axis=0)
                y_train = np.concatenate((y_train_good, y_train_bad, y_train_add), axis=0)
                y_test = np.concatenate((y_test_good, y_test_bad, y_test_add), axis=0)

            # -- train ML model
            # ................................................................

            # training the model
            self.model.fit(X_Train, y_train)
            self.model_trained = 1

            # run test data
            predictions = self.model.predict(X_Test)

            # calculate score
            score = accuracy_score(y_test, predictions)

            #print('****** Accuracy', score)
            #self.logger.print(f'**** Amount of train {np.shape(X_Train)} vs amount of test {np.shape(X_Test)} data with accuracy {score}.****')

            self.logger.print('AIMon! Score of training: ' +str(score*100) + '%.')

            # -- Further analysis
            # ................................................................

            results = np.zeros(shape=(3, 2), dtype=np.float32)

            for i in range(0, len(y_test)):

                class_id = int(y_test[i])

                if  class_id == predictions[i]:
                    results[class_id, 0] += 1
                else:
                    results[class_id, 1] += 1

            self.logger.print('AIMon! Test results for good signals. Correct: ' + str(results[0,0]) + ' false: ' + str(results[0,1]) + '.')
            self.logger.print('AIMon! Test results for bad signals. Correct: ' + str(results[1,0]) + ' false: ' + str(results[1,1]) + '.')
            self.logger.print('AIMon! Test results for add signals. Correct: ' + str(results[2,0]) + ' false: ' + str(results[2,1]) + '.')

            time_02 = time.time()
            self.logger.print('AIMon! Runtime for AI training: {:8.6f}s'.format(time_02-time_01))

        # --------------------------------------------------------

        elif self.state == 'save_model':

            if self.model_trained == 0:
                self.logger.print('AIMon! ERROR - AI model NOT trained and NOT stored.')
            else:
                try:
                    dump(self.model, self.modelPath)
                    self.logger.print('AIMon! AI model saved.')
                except Error:
                    self.logger.print('AIMon! ERROR while saving AI model!')

        # --------------------------------------------------------

        elif self.state == 'load_model':

            if not path.exists(self.modelPath):
                self.logger.print('AIMon! ERROR file with AI model does not exist!')
            else:
                try:
                    self.model = load(self.modelPath)
                    self.logger.print('AIMon! AI model loaded.')
                    self.model_trained = 1
                except Error:
                    self.logger.print('AIMon! ERROR while loading AI model!')

        # --------------------------------------------------------
        elif self.state == 'purge_db':

            deleteTableStatement = f'DELETE FROM {self.tablename}'

            # delete table
            try:
                c = self.db_conn.cursor()
                c.execute(deleteTableStatement)
                self.db_conn.commit()
                self.logger.print('AIMon! Table cleared.')
            except Error:
                self.logger.print('AIMon! ERROR while deleting stored data!')

            try:
                self.db_conn.execute('vacuum')
                self.db_conn.commit()
                self.logger.print('AIMon! DB cleared.')
            except Error:
                self.logger.print('AIMon! ERROR while clear db.')

            self.logger.print('AIMon! Collected data deleted.')

        # --------------------------------------------------------

        elif self.state in ['purge_db_good', 'purge_db_bad', 'purge_db_add']:

            if self.state == 'purge_db_good':
                data_class = 0
            elif self.state == 'purge_db_bad':
                data_class = 1
            elif self.state == 'purge_db_add':
                data_class = 2
            
            deleteTableStatement = f'DELETE FROM {self.tablename} WHERE classid = {data_class}'

            # delete data from table
            try:
                c = self.db_conn.cursor()
                c.execute(deleteTableStatement)
                self.db_conn.commit()
                self.logger.print(f'AIMon! {self.state} completed.')
            except Error:
                self.logger.print(f'AIMon! ERROR while {self.state}')

        # --------------------------------------------------------
        close_connection(self.db_conn)

    # ========================================================
    # ========================================================
