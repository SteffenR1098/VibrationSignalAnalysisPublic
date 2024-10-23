'''
    Script to generate and save simulated test data.
    There are three different types of data signals each with 1000 entities.
    Each data signal itself has a length of 4096 values.
    The different data signals are created by frequency spikes with a certain amplitued that are varied within an interval and shuffeled. 
    The signals are then blurred with convolution masks and background and noise is added.
    The "good" and "bad" signals are easy distinguishable. But the "additional" signals are just a small variation of the good signal with one small additional ampliude.
'''


import random
#from pathlib import Path
import numpy as np
#import matplotlib.pyplot as plt
from scipy.fftpack import fft
import time
import sqlite3
from sqlite3 import Error
#from sys import getsizeof

#from db_functions import create_connection, show_tables, show_data, show_some_data, commit_data, delete_data, close_connection
#from db_blob_functions import insert_blob_data, get_blob_data

from helper_functions import get_db_parameter, get_fft_values, get_parameter
from helper_db_functions import create_connection, show_tables, insert_blob_data, commit_data, delete_data, close_connection

# ========================================================
# ====  Parameter  =======================================
# ========================================================

# === DB parameter ===
source_db_file = get_db_parameter('source_db_file')
source_table_name = get_db_parameter('source_table_name')

# ==== variable signal parameter ====
amount_of_signals = get_parameter('amount_of_signals')
print(f'Amount of signals: {amount_of_signals}')

good_first_peak_low = get_parameter('good_first_peak_low')
good_first_peak_high = get_parameter('good_first_peak_high')

good_second_peak_low = get_parameter('good_second_peak_low')
good_second_peak_high = get_parameter('good_second_peak_high')

good_third_peak_low = get_parameter('good_third_peak_low')
good_third_peak_high = get_parameter('good_third_peak_high')

bad_first_peak_low = get_parameter('bad_first_peak_low')
bad_first_peak_high = get_parameter('bad_first_peak_high')

bad_second_peak_low = get_parameter('bad_second_peak_low')
bad_second_peak_high = get_parameter('bad_second_peak_high')

bad_third_peak_low = get_parameter('bad_third_peak_low')
bad_third_peak_high = get_parameter('bad_third_peak_high')

add_fourth_peak_low = get_parameter('add_fourth_peak_low')
add_fourth_peak_high = get_parameter('add_fourth_peak_high')

first_amplitudes_good_low = get_parameter('first_amplitudes_good_low')
first_amplitudes_good_high = get_parameter('first_amplitudes_good_high')

second_amplitudes_good_low = get_parameter('second_amplitudes_good_low')
second_amplitudes_good_high = get_parameter('second_amplitudes_good_high')

third_amplitudes_good_low = get_parameter('third_amplitudes_good_low')
third_amplitudes_good_high = get_parameter('third_amplitudes_good_high')

first_amplitudes_bad_low = get_parameter('first_amplitudes_bad_low')
first_amplitudes_bad_high = get_parameter('first_amplitudes_bad_high')

second_amplitudes_bad_low = get_parameter('second_amplitudes_bad_low')
second_amplitudes_bad_high = get_parameter('second_amplitudes_bad_high')

third_amplitudes_bad_low = get_parameter('third_amplitudes_bad_low')
third_amplitudes_bad_high = get_parameter('third_amplitudes_bad_high')

fourth_amplitudes_add_low = get_parameter('fourth_amplitudes_add_low')
fourth_amplitudes_add_high = get_parameter('fourth_amplitudes_add_high')

# ==== fixed parameter  for FFT and signal degradation with noise and convolutiom ====

t_n = 3.28
N = 8192
T = t_n / N
f_s = 1/T

amount_of_values = 4096

factor_conv_mask1 = 1.5
factor_conv_mask2 = 1.35

mask1 = [0.05, 0.15, 0.6, 0.15, 0.05]
mask2 = [0.1, 0.8, 0.1]

noise_strength = 1.1

# ========================================================

# ==== parameter good signal =====

first_frequencies_good = list(range(good_first_peak_low, good_first_peak_high, int((good_first_peak_high-good_first_peak_low) / amount_of_signals)))
second_frequencies_good = list(range(good_second_peak_low, good_second_peak_high, int((good_second_peak_high-good_second_peak_low) / amount_of_signals)))
third_frequencies_good = list(range(good_third_peak_low, good_third_peak_high, int((good_third_peak_high-good_third_peak_low) / amount_of_signals)))

# ==== parameter bad signal =====

first_frequencies_bad = list(range(bad_first_peak_low, bad_first_peak_high, int((bad_first_peak_high-bad_first_peak_low) / amount_of_signals)))
second_frequencies_bad = list(range(bad_second_peak_low, bad_second_peak_high, int((bad_second_peak_high-bad_second_peak_low) / amount_of_signals)))
third_frequencies_bad = list(range(bad_third_peak_low, bad_third_peak_high, int((bad_third_peak_high-bad_third_peak_low) / amount_of_signals)))

# ==== parameter add signal =====

# later float and /100
first_frequencies_add = list(range(good_first_peak_low, good_first_peak_high, int((good_first_peak_high-good_first_peak_low) / amount_of_signals)))
# later float and /10
second_frequencies_add = list(range(good_second_peak_low, good_second_peak_high, int((good_second_peak_high-good_second_peak_low) / amount_of_signals)))
third_frequencies_add = list(range(good_third_peak_low, good_third_peak_high, int((good_third_peak_high-good_third_peak_low) / amount_of_signals)))
# later float and /100
fourth_frequencies_add = list(range(add_fourth_peak_low, add_fourth_peak_high, int((add_fourth_peak_high-add_fourth_peak_low) / amount_of_signals)))

# ========================================================
# ====  Creating good signal =============================
# ========================================================

time_01 = time.time()

# x values: start, stop, amount of steps
x_value = np.linspace(0, t_n, N, endpoint=True)

# ==== creating good signals ====

fft_values_total = np.zeros(shape=(amount_of_signals, amount_of_values))

first_amplitudes_good_low = int(abs(first_amplitudes_good_low*factor_conv_mask1))
first_amplitudes_good_high = int(abs(first_amplitudes_good_high*factor_conv_mask1))

second_amplitudes_good_low = int(abs(second_amplitudes_good_low*factor_conv_mask1))
second_amplitudes_good_high = int(abs(second_amplitudes_good_high*factor_conv_mask1))

third_amplitudes_good_low = int(abs(third_amplitudes_good_low*factor_conv_mask2))
third_amplitudes_good_high = int(abs(third_amplitudes_good_high*factor_conv_mask2))

first_amplitudes_good = list(range(first_amplitudes_good_low, first_amplitudes_good_high, int((first_amplitudes_good_high-first_amplitudes_good_low)/amount_of_signals)))
second_amplitudes_good = list(range(second_amplitudes_good_low, second_amplitudes_good_high, int((second_amplitudes_good_high-second_amplitudes_good_low)/amount_of_signals)))
third_amplitudes_good = list(range(third_amplitudes_good_low, third_amplitudes_good_high, int((third_amplitudes_good_high-third_amplitudes_good_low)/amount_of_signals)))

# shuffle amplitudes and frequencies
random.shuffle(first_amplitudes_good)
random.shuffle(second_amplitudes_good)
random.shuffle(third_amplitudes_good)
random.shuffle(first_frequencies_good)
random.shuffle(second_frequencies_good)
random.shuffle(third_frequencies_good)

for it in range(0, amount_of_signals):
    amplitudes = [first_amplitudes_good[it], second_amplitudes_good[it],third_amplitudes_good[it]]  # amplitude of FFT
    frequencies = [first_frequencies_good[it]/100, second_frequencies_good[it]/10, third_frequencies_good[it]/10]  # peaks at points in HZ

    y_values = [amplitudes[ii]*np.sin(2*np.pi*frequencies[ii]*x_value)
                for ii in range(0, len(amplitudes))]

    comp_y_value = np.sum(y_values, axis=0)

    # ==== FFT ====
    f_values, fft_values = get_fft_values(comp_y_value, T, N, f_s)

    # ==== modify FFT background ====

    fft_values_background = fft_values.copy()

    for index in range(0, 100):
        fft_values_background[index] += 460 * \
            (index**2) - 93000 * index + 5000000

    fft_values_background[100:900] += 300000
    fft_values_background[900:1100] += 200000
    fft_values_background[1100:1300] += 150000
    fft_values_background[1300:2000] += 80000
    fft_values_background[2000:] += 30000

    # ==== modify FFT conv ====
    fft_values_conv = fft_values_background.copy()
    fft_values_conv[:1800] = np.convolve(
        fft_values_background[:1800], mask1, 'same')
    fft_values_conv[1800:] = np.convolve(
        fft_values_background[1800:], mask2, 'same')

    # ==== modify FFT noise ====
    fft_values_rand = fft_values_conv.copy()
    factor = -1.0
    noise_base_default = 5000000

    for item in range(0, len(fft_values_conv)):
        factor *= -1.0
        noise_base = min(abs(round(fft_values_conv[item])), noise_base_default)
        noise_value = random.randint(1, noise_base) * noise_strength
        fft_values_rand[item] = abs(
            fft_values_conv[item] + factor * noise_value)

    fft_values_total[it] = fft_values_rand

#print(f'Type: {type(fft_values_total)} and shape {np.shape(fft_values_total)} of FFT values.')

time_02 = time.time()
print('Runtime to generate "good" signals: {:8.6f}s'.format(time_02-time_01))

# ========================================================
# ====  creating bad signal data =========================
# ========================================================

fft_values_total_bad = np.zeros(shape=(amount_of_signals, amount_of_values))

first_amplitudes_bad_low = int(abs(first_amplitudes_bad_low*factor_conv_mask1))
first_amplitudes_bad_high = int(abs(first_amplitudes_bad_high*factor_conv_mask1))

second_amplitudes_bad_low = int(abs(second_amplitudes_bad_low*factor_conv_mask1))
second_amplitudes_bad_high = int(abs(second_amplitudes_bad_high*factor_conv_mask1))

third_amplitudes_bad_low = int(abs(third_amplitudes_bad_low*factor_conv_mask2))
third_amplitudes_bad_high = int(abs(third_amplitudes_bad_high*factor_conv_mask2))

first_amplitudes_bad = list(range(first_amplitudes_bad_low, first_amplitudes_bad_high, int((first_amplitudes_bad_high-first_amplitudes_bad_low)/amount_of_signals)))
second_amplitudes_bad = list(range(second_amplitudes_bad_low, second_amplitudes_bad_high, int((second_amplitudes_bad_high-second_amplitudes_bad_low)/amount_of_signals)))
third_amplitudes_bad = list(range(third_amplitudes_bad_low, third_amplitudes_bad_high, int((third_amplitudes_bad_high-third_amplitudes_bad_low)/amount_of_signals)))

# shuffle amplitudes and frequencies
random.shuffle(first_amplitudes_bad)
random.shuffle(second_amplitudes_bad)
random.shuffle(third_amplitudes_bad)
random.shuffle(first_frequencies_bad)
random.shuffle(second_frequencies_bad)
random.shuffle(third_frequencies_bad)

for it in range(0, amount_of_signals):
    amplitudes_bad = [first_amplitudes_bad[it], second_amplitudes_bad[it],third_amplitudes_bad[it]]  # amplitude of FFT
    frequencies_bad = [first_frequencies_bad[it]/10, second_frequencies_bad[it]/10, third_frequencies_bad[it]/10]  # peaks at points in HZ

    y_values_bad = [amplitudes_bad[ii]*np.sin(2*np.pi*frequencies_bad[ii]*x_value)
                    for ii in range(0, len(amplitudes_bad))]

    comp_y_value_bad = np.sum(y_values_bad, axis=0)

    # ==== FFT ====
    f_values_bad, fft_values_bad = get_fft_values(comp_y_value_bad, T, N, f_s)

    # ==== modify FFT background ====

    fft_values_bad_background = fft_values_bad.copy()

    fft_values_bad_background[:900] += 300000
    fft_values_bad_background[900:1100] += 200000
    fft_values_bad_background[1100:1300] += 150000
    fft_values_bad_background[1300:2000] += 80000
    fft_values_bad_background[2000:] += 30000

    # ==== modify FFT conv ====
    fft_values_bad_conv = fft_values_bad_background.copy()
    fft_values_bad_conv[:1800] = np.convolve(
        fft_values_bad_background[:1800], mask1, 'same')
    fft_values_bad_conv[1800:] = np.convolve(
        fft_values_bad_background[1800:], mask2, 'same')

    # ==== modify FFT noise ====
    fft_values_bad_rand = fft_values_bad_conv.copy()
    factor = -1.0
    noise_base_default = 5000000

    for item in range(0, len(fft_values_bad_conv)):
        factor *= -1.0
        noise_base = min(
            abs(round(fft_values_bad_conv[item])), noise_base_default)
        noise_value = random.randint(1, noise_base) * noise_strength
        fft_values_bad_rand[item] = abs(
            fft_values_bad_conv[item] + factor * noise_value)

    fft_values_total_bad[it] = fft_values_bad_rand

# print(f'Type: {type(fft_values_total_bad)} and shape {np.shape(fft_values_total_bad)} of bad FFT values.')

time_03 = time.time()
print('Runtime to generate "bad" signals: {:8.6f}s'.format(time_03-time_02))


# ========================================================
# ====  Create additional data ===========================
# ========================================================

first_amplitudes_add_low = int(abs(first_amplitudes_good_low*factor_conv_mask1))
first_amplitudes_add_high = int(abs(first_amplitudes_good_high*factor_conv_mask1))

second_amplitudes_add_low = int(abs(second_amplitudes_good_low*factor_conv_mask1))
second_amplitudes_add_high = int(abs(second_amplitudes_good_high*factor_conv_mask1))

third_amplitudes_add_low = int(abs(third_amplitudes_good_low*factor_conv_mask2))
third_amplitudes_add_high = int(abs(third_amplitudes_good_high*factor_conv_mask2))

fourth_amplitudes_add_low = int(abs(fourth_amplitudes_add_low*factor_conv_mask2))
fourth_amplitudes_add_high = int(abs(fourth_amplitudes_add_high*factor_conv_mask2))

# ========================================================

fft_values_total_add = np.zeros(shape=(amount_of_signals, amount_of_values))

first_amplitudes_add = list(range(first_amplitudes_add_low, first_amplitudes_add_high, int((first_amplitudes_add_high-first_amplitudes_add_low)/amount_of_signals)))
second_amplitudes_add = list(range(second_amplitudes_add_low, second_amplitudes_add_high, int((second_amplitudes_add_high-second_amplitudes_add_low)/amount_of_signals)))
third_amplitudes_add = list(range(third_amplitudes_add_low, third_amplitudes_add_high, int((third_amplitudes_add_high-third_amplitudes_add_low)/amount_of_signals)))
fourth_amplitudes_add = list(range(fourth_amplitudes_add_low, fourth_amplitudes_add_high, int((fourth_amplitudes_add_high-fourth_amplitudes_add_low)/amount_of_signals)))

random.shuffle(first_amplitudes_add)
random.shuffle(second_amplitudes_add)
random.shuffle(third_amplitudes_add)
random.shuffle(fourth_amplitudes_add)
random.shuffle(first_frequencies_add)
random.shuffle(second_frequencies_add)
random.shuffle(third_frequencies_add)
random.shuffle(fourth_frequencies_add)

index_min = 0

for it in range(0, amount_of_signals):
    if first_frequencies_add[it] == min(first_frequencies_add):
        index_min = it

    amplitudes_add = [first_amplitudes_add[it], second_amplitudes_add[it], third_amplitudes_add[it], fourth_amplitudes_add[it]]  # amplitude of FFT
    frequencies_add = [first_frequencies_add[it]/100, second_frequencies_add[it]/10, third_frequencies_add[it]/10, fourth_frequencies_add[it]/100]  # peaks at points in HZ

    y_values_add = [amplitudes_add[ii]*np.sin(2*np.pi*frequencies_add[ii]*x_value)
                    for ii in range(0, len(amplitudes_add))]

    #print(f'Shape of y: {np.shape(y_values_add)}, type of {type(y_values_add)}')
    comp_y_value = np.sum(y_values_add, axis=0)

    # ==== FFT ====

    f_values, fft_values_add = get_fft_values(comp_y_value, T, N, f_s)

    # ==== modify FFT background ====

    fft_values_add_background = fft_values_add.copy()

    for index in range(0, 100):
        fft_values_add_background[index] += 460 * \
            (index**2) - 93000 * index + 5000000

    fft_values_add_background[100:900] += 300000
    fft_values_add_background[900:1100] += 200000
    fft_values_add_background[1100:1300] += 150000
    fft_values_add_background[1300:2000] += 80000
    fft_values_add_background[2000:] += 30000

    # ==== modify FFT conv ====
    fft_values_add_conv = fft_values_add_background.copy()
    fft_values_add_conv[:1800] = np.convolve(
        fft_values_add_background[:1800], mask1, 'same')
    fft_values_add_conv[1800:] = np.convolve(
        fft_values_add_background[1800:], mask2, 'same')

    # ==== modify FFT noise ====
    fft_values_add_rand = fft_values_add_conv.copy()
    factor = -1.0
    strength = 1.1
    noise_base_default = 5000000

    for item in range(0, len(fft_values_add_conv)):
        factor *= -1.0
        noise_base = min(
            abs(round(fft_values_add_conv[item])), noise_base_default)
        noise_value = random.randint(1, noise_base) * strength
        fft_values_add_rand[item] = abs(
            fft_values_add_conv[item] + factor * noise_value)

    fft_values_total_add[it] = fft_values_add_rand

time_031 = time.time()
print('Runtime to generate "add" signals: {:8.6f}s'.format(time_031-time_03))

# ========================================================
# ====  Save data into DB ================================
# ========================================================

print('-------------------------------------------')
print('Saving data to DB as blob.')

# == open db connection
db_conn = create_connection(source_db_file)

if db_conn:

    # === check all tables in DB
    show_tables(db_conn)

    # === delete all data
    delete_data(db_conn, source_table_name)

    # === convert to float32
    fft_values_total_32 = np.float32(fft_values_total)
    fft_values_total_bad_32 = np.float32(fft_values_total_bad)
    fft_values_total_add_32 = np.float32(fft_values_total_add)

    # === Used to insert data

    data_class = 0
    insert_blob_data(db_conn, source_table_name, fft_values_total_32, data_class)

    data_class = 1
    insert_blob_data(db_conn, source_table_name, fft_values_total_bad_32, data_class)

    data_class = 2
    insert_blob_data(db_conn, source_table_name, fft_values_total_add_32, data_class)

    # == commit all changes
    commit_data(db_conn)

close_connection(db_conn)

time_04 = time.time()

print('Runtime to store data in DB: {:8.6f}s'.format(time_04-time_031))
print('Total runtime for data: {:8.6f}s'.format(time_04-time_01))

print('End.')
