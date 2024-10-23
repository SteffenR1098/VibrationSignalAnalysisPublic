'''
    Script to visualize some data sets for good, bad and additional data
'''

import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from sqlite3 import Error

from helper_functions import get_db_parameter
from helper_db_functions import create_connection, show_tables, get_blob_data, close_connection

# ========================================================
# ====  Parameter  =======================================
# ========================================================

# === DB parameter ===
source_db_file = get_db_parameter('source_db_file')
source_table_name = get_db_parameter('source_table_name')

# ========================================================
# ====  load data from DB ================================
# ========================================================

print('-------------------------------------------')
print('Load data to DB as blob.')

# == open db connection
db_conn = create_connection(source_db_file)

if db_conn:

    # === check all tables in DB
    show_tables(db_conn)

    # === Used to insert data
    data_class = 0
    fft_values_total = get_blob_data(db_conn, source_table_name, data_class)

    data_class = 1
    fft_values_total_bad = get_blob_data(db_conn, source_table_name, data_class)

    data_class = 2
    fft_values_total_add = get_blob_data(db_conn, source_table_name, data_class)

close_connection(db_conn)

# Check data
print(type(fft_values_total), np.shape(fft_values_total))
print(type(fft_values_total_bad), np.shape(fft_values_total_bad))
print(type(fft_values_total_add), np.shape(fft_values_total_add))

fft_values_total_32 = np.float32(fft_values_total)
fft_values_total_bad_32 = np.float32(fft_values_total_bad)
fft_values_total_add_32 = np.float32(fft_values_total_add)

# ========================================================
# ====  Show some examples ===============================
# ========================================================

f_values = range(0, 4096)
# print(fft_values_add_total[0:10][0:10])

plt.figure(11)
plt.plot(f_values, fft_values_total[0], 'b-')
plt.xlabel('Frequency [Hz]', fontsize=12)
plt.ylabel('Amplitude', fontsize=12)
plt.title("FFT of generated signal", fontsize=12)
#plt.show()

plt.figure(12)
plt.plot(f_values, fft_values_total_add[0], 'b-')
plt.xlabel('Frequency [Hz]', fontsize=12)
plt.ylabel('Amplitude', fontsize=12)
plt.title("FFT of signal with addition peak", fontsize=12)
#plt.show()

plt.figure(13)
plt.plot(f_values, fft_values_total_bad[0], 'b-')
plt.xlabel('Frequency [Hz]', fontsize=12)
plt.ylabel('Amplitude', fontsize=12)
plt.title("FFT of 'bad' signal", fontsize=12)
#plt.show()

plt.figure(1)
plt.plot(f_values, fft_values_total[0], 'b-')
plt.plot(f_values, fft_values_total[12], 'k:')
plt.plot(f_values, fft_values_total[400], 'g-.')
plt.xlabel('Frequency [Hz]', fontsize=12)
plt.ylabel('Amplitude', fontsize=12)
plt.title("FFT of good signals", fontsize=12)
#plt.show()

plt.figure(2)
plt.plot(f_values, fft_values_total_bad[0], 'b-')
plt.plot(f_values, fft_values_total_bad[12], 'k:')
plt.plot(f_values, fft_values_total_bad[400], 'g-.')
plt.xlabel('Frequency [Hz]', fontsize=12)
plt.ylabel('Amplitude', fontsize=12)
plt.title("FFT of bad signals", fontsize=12)
#plt.show()

plt.figure(3)
plt.plot(f_values, fft_values_total_add[0], 'b-')
plt.plot(f_values, fft_values_total_add[12], 'k:')
plt.plot(f_values, fft_values_total_add[400], 'g-.')
plt.xlabel('Frequency [Hz]', fontsize=12)
plt.ylabel('Amplitude', fontsize=12)
plt.title("FFT of signal with addition peak", fontsize=12)
plt.show()

print('End.')