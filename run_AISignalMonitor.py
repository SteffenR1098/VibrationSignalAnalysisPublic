'''
    Script to run simulated scenario using AISignalMonitor and AISignalProducer.
    Collecting data, training ML model and simulating operational mode for all signal data classes.
'''
from AISignalMonitor import AISignalMonitor
from AISignalProducer import AISignalProducer
from AImonitorLogger import AImonitorLogger
from ProducerLogger import ProducerLogger

import time

# ========================================================

from helper_functions import get_db_parameter, get_AI_parameter, get_operational_parameter

# ========================================================
# get parameter for dbs, tables and file to store trained AI model

source_db_file = get_db_parameter('source_db_file')
source_table_name = get_db_parameter('source_table_name')

monitor_db_file = get_db_parameter('monitor_db_file')
monitor_table_name = get_db_parameter('monitor_table_name')

model_file = get_AI_parameter('model_file')

sleep_time_operational = get_operational_parameter('operational_wait_time')

purge_db = 0

# ========================================================

AImonitorLog = AImonitorLogger()
Dumlogprod = ProducerLogger()

# ========================================================

AIProd = AISignalProducer('good', source_db_file, source_table_name, Dumlogprod)
AImon = AISignalMonitor('collecting_good', monitor_db_file, monitor_table_name, model_file, AImonitorLog)

# ========================================================

AImon.onStateChange('check_stored_data')
AImon.onStateChange('purge_db')
AImon.onStateChange('check_stored_data')

# ========================================================

AIProd.onStateChange('good')
AImon.onStateChange('collecting_good')

for i in range(0, 400):
    data = AIProd.onFrame()
    AImon.onSignal(data)

# ========================================================

AImon.onStateChange('check_stored_data')

# ========================================================

AIProd.onStateChange('bad')
AImon.onStateChange('collecting_bad')

for i in range(0, 400):
    data = AIProd.onFrame()
    AImon.onSignal(data)

# ========================================================

AImon.onStateChange('check_stored_data')

# ========================================================

AIProd.onStateChange('additional')
AImon.onStateChange('collecting_additional')

for i in range(0, 400):
    data = AIProd.onFrame()
    AImon.onSignal(data)

# ========================================================

AImon.onStateChange('check_stored_data')

# ========================================================

AImon.onStateChange('train')

# ========================================================

if purge_db == 1:
    AImon.onStateChange('check_stored_data')
    AImon.onStateChange('purge_db_good')
    AImon.onStateChange('check_stored_data')
    AImon.onStateChange('purge_db_bad')
    AImon.onStateChange('check_stored_data')
    AImon.onStateChange('purge_db_add')
    AImon.onStateChange('check_stored_data')

# ========================================================

AImon.onStateChange('evaluate')

AIProd.onStateChange('good')
print('run-script: Evaluating good signals.')
for i in range(0, 10):
    data = AIProd.onFrame()
    AImon.onSignal(data)   
    time.sleep(sleep_time_operational)

AIProd.onStateChange('bad')
print('run-script: Evaluating bad signals.')
for i in range(0, 10):
    data = AIProd.onFrame()
    AImon.onSignal(data)
    time.sleep(sleep_time_operational)

AIProd.onStateChange('additional')
print('run-script: Evaluating additional signals.')
for i in range(0, 10):
    data = AIProd.onFrame()
    AImon.onSignal(data)
    time.sleep(sleep_time_operational)

# ========================================================

#AImon.onStateChange('save_model')

# ========================================================

print('=== Ende! ===')