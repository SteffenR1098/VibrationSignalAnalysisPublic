'''
    Py file to store and provide parameter
'''
# ========================================================
# Get db parameter

def get_db_parameter(param_type):

    if param_type == 'db_source_file':
        return r'DBs\datasource.db'
    elif param_type == 'source_table_name':
        return 'source_data_table'
    elif param_type == 'db_monitor_file':
        return r'DBs\AImonitor.db'
    elif param_type == 'monitor_table_name':
        return 'monitor_data_table'
    else:
        return None

# ========================================================
# Get parameter for data generation

def get_parameter(param_type):

    if param_type == 'amount_of_signals':
        return 1000
    elif param_type == 'ratio_test_train':
        # amount of data to used for tests
        return 0.8
    elif param_type == 'ratio_test_train_anomaly':
        # amount of data to used for tests
        return 0.2
    elif param_type == 'first_peak_low':
        # /100
        return 100
    elif param_type == 'first_peak_high':
        # /100
        return 3000
    elif param_type == 'fourth_peak_low':
        # /100
        return 6000
    elif param_type == 'fourth_peak_high':
        # /100
        return 8000
    # elif param_type == '':
    else:
        return None


# ========================================================
# FFT function


def get_fft_values(y_values, T, N, f_s):

    import numpy as np
    from scipy.fftpack import fft

    f_values = np.linspace(0.0, 1.0/(2.0*T), N//2)
    fft_values_ = fft(y_values)
    fft_values = 2.0/N * np.abs(fft_values_[0:N//2])
    return f_values, fft_values


# ========================================================
# PSD Power Spectral Density


def get_psd_values(y_values, T, N, f_s):

    from scipy.signal import welch

    f_values, psd_values = welch(y_values, fs=f_s)
    return f_values, psd_values


# ========================================================
