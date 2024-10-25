'''
    Simulate a data source that is similar to a vibration sensor and FFT module observing a rotation part.
'''

# ========================================================
# imports

import numpy as np
from sqlite3 import Error
import time

# ========================================================
# own imports

from helper_db_functions import trans_ndarray2blob, trans_blob2ndarray, state_is_UTF8, create_connection, close_connection
from helper_functions import get_operational_parameter, get_parameter

# ========================================================

class AISignalProducer():
    '''
        class to simulate data source. A vibration sensor and FFT module would provide data in a similar way
        methods: __init__: class constructor. Initialization including loading all data from the data source SQLite DB 
                 __del__: class descructor
                 onFrame: iteration of providing data in working mode
                 onStateChange: change state of Producer to provide different kinds of data
    '''
    # ========================================================
    # ========================================================

    def __init__(self, state, dbPath, tablename, logger):
        '''
            class constructor: 
            - setting initial state, variables, indices an counters
            - loading all available data from db

        '''

        # setting variables
        self.dbPath = dbPath
        self.tablename = tablename

        self.logger = logger

        # the following states are allowed for the Producer - will be used in setting initial state and in onStateChange method
        self.allowed_states = ['good', 'bad', 'additional']

        self.wait_time = get_operational_parameter('producer_wait_time')

        self.logger.print('AIProd! Initialize.')

        if state in self.allowed_states:
            self.state = state
            self.logger.stateChange('AIProd! Initial state set: ' + state + '.')
        else:
            self.logger.print('AIProd! WARNING: New state was not valid. Default to good.')
            self.state = 'good'

        self.data_good = None
        self.data_bad = None
        self.data_add= None

        self.data_good_index = 0
        self.data_bad_index = 0
        self.data_add_index = 0

        self.data_good_size = 0
        self.data_bad_size = 0
        self.data_add_size = 0

        self.amount_floats = get_parameter('signal_length')

        self.counter = 0
        self.state_change = 0

        self.data_counter = 0
        # maximum amount of signals provided for each state change
        self.max_data  = get_operational_parameter('max_data_producer')

        # The message given to the Logger will be alterated to see progress for a huge number of calls of "onFrame" method
        self.show_progress = 0

        # --------------------------------------
        # Connect to db table
        # --------------------------------------

        self.logger.print('AIProd! Loading data from DB.')

        # == open db connection
        self.db_conn = create_connection(self.dbPath)

        if self.db_conn:

            # --------------------------------------
            # Load good data from db table
            # --------------------------------------

            data_class = 0

            sql_getdata_command = f'SELECT * FROM {self.tablename} WHERE classid = {data_class}'

            try:
                cur = self.db_conn.cursor()
                cur.execute(sql_getdata_command)
                rows = cur.fetchall()
            except Error:
                self.logger.print('AIProd! ERROR: good data not loaded.')

            self.data_good_size = np.shape(rows)[0]

            self.data_good = np.zeros(shape=(self.data_good_size, self.amount_floats), dtype=np.float32)

            index = 0
            for row in rows:
                self.data_good[index, :] = trans_blob2ndarray(row[2])
                index += 1

            # --------------------------------------
            # Load bad data from db table
            # --------------------------------------

            data_class = 1

            sql_getdata_command = f'SELECT * FROM {self.tablename} WHERE classid = {data_class}'

            try:
                cur.execute(sql_getdata_command)
                rows = cur.fetchall() 
            except Error:
                self.logger.print('AIProd! ERROR: bad data not loaded.')

            self.data_bad_size = np.shape(rows)[0]

            self.data_bad = np.zeros(shape=(self.data_bad_size, self.amount_floats), dtype=np.float32)

            index = 0
            for row in rows:
                self.data_bad[index, :] = trans_blob2ndarray(row[2])
                index += 1

            # --------------------------------------
            # Load additional data from db table
            # --------------------------------------

            data_class = 2

            sql_getdata_command = f'SELECT * FROM {self.tablename} WHERE classid = {data_class}'

            try:
                cur.execute(sql_getdata_command)
                rows = cur.fetchall() 
            except Error:
                self.logger.print('AIProd! ERROR: additional data not loaded.')

            self.data_add_size = np.shape(rows)[0]

            self.data_add = np.zeros(shape=(self.data_add_size, self.amount_floats), dtype=np.float32)

            index = 0
            for row in rows:
                self.data_add[index, :] = trans_blob2ndarray(row[2])
                index += 1

        else:
            self.logger.print('AIProd! ERROR Problem with db connection.')

        # --------------------------------------
        # Close db connection
        # --------------------------------------
        close_connection(self.db_conn)

        self.logger.print('AIProd! Initialize completed.')

    # ========================================================
    # ========================================================

    def __del__(self):
        '''
            Class destructor
        '''
        self.logger.print('AIProd! End.')

    # ========================================================
    # ========================================================

    def onFrame(self):
        '''
            method to simulate iteration of providing data signal in working mode
            returns signal depending on state of class and counter.
        '''

        if self.state_change == 1:
            # state was changed. Re-initialize counters and simulate waiting time.
            self.logger.print(f'AIProd!! state change - wait {self.wait_time} sec.')
            self.state_change = 0
            self.data_counter = 0
            time.sleep(self.wait_time)

        # Send a message to Logger every 50 iterations to show progress and alternate messages
        if self.counter >= 49:
            if self.data_counter < self.max_data:
                if self.show_progress == 0:
                    self.show_progress = 1
                    self.logger.print(f'AIProd!! onFrame ({self.state}) - 50.')
                else:
                    self.show_progress = 0
                    self.logger.print(f'AIProd!! onFrame ({self.state}) - 50 x.')
            else:
                if self.show_progress == 0:
                    self.show_progress = 1
                    self.logger.print('AIProd!! onFrame - 50 - no signal.')
                else:
                    self.show_progress = 0
                    self.logger.print('AIProd!! onFrame - 50 - no signal x.')

            self.counter = 0
        else:
            self.counter += 1

        data_return = None

        if self.data_counter < self.max_data:
            self.data_counter += 1

            # --------------------------------------------------------
            if self.state == 'good':

                #self.logger.print(f'!!!! onFrame in state: {self.state} !!!!')

                data_return = self.data_good[self.data_good_index,:]

                self.data_good_index += 1
                if self.data_good_index >= self.data_good_size:
                    self.data_good_index = 0

            # --------------------------------------------------------
            elif self.state == 'bad':

                #self.logger.print(f'!!!! bad onFrame in state: {self.state} !!!!')
                data_return = self.data_bad[self.data_bad_index,:]

                self.data_bad_index += 1
                if self.data_bad_index >= self.data_bad_size:
                    self.data_bad_index = 0

            # --------------------------------------------------------
            elif self.state == 'additional':

                #self.logger.print(f'!!!! bad onFrame in state: {self.state} !!!!')
                data_return = self.data_add[self.data_add_index,:]

                self.data_add_index += 1
                if self.data_add_index >= self.data_add_size:
                    self.data_add_index = 0

	    # --------------------------------------------------------
            else:
                self.logger.print('AIProd! WARNING: onFrame - Unkown state.')

        return data_return

    # ========================================================
    # ========================================================

    def onStateChange(self, state):
        '''
            method to change state of class with utf-8 check and logger message
        '''

        self.logger.stateChange('AIProd! Changing state.')

        self.state_change = 1

        if state_is_UTF8(state):
            state_new = state.decode('utf-8')
        else:
            state_new = state

        if state_new in self.allowed_states:
            self.state = state_new
            self.logger.stateChange('AIProd! State changed: ' + state_new + '.')
        else:
            self.logger.stateChange('AIProd! WARNING: New state was not valid.')

        #self.logger.stateChange('AIProd! Changing state. End.')

    # ========================================================
    # ========================================================
