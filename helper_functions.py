'''
    Py file to store and provide parameter
'''
# ========================================================
# Get db parameter

def get_db_parameter(param_type):

    if param_type == 'source_db_file':
        return r'DBs\datasource.db'
    elif param_type == 'source_table_name':
        return 'source_data_table'
    elif param_type == 'monitor_db_file':
        return r'DBs\AImonitor.db'
    elif param_type == 'monitor_table_name':
        return 'monitor_data_table'
    else:
        return None
    
# ========================================================
# Get AI parameter

def get_AI_parameter(param_type):

    #print('get_AI_parameter')
    #print(param_type)
    
    if param_type == 'model_file':
        return r'SaveMLModel\model.ai'
    elif param_type == 'test_train_split':
        return 0.5
    else:
        return None

# ========================================================
# Get parameter for data generation

def get_operational_parameter(param_type):

    if param_type == 'producer_wait_time':
        return 3 #in seconds
    elif param_type == 'operational_wait_time':
        return 0 #in seconds
    elif param_type == 'max_data_producer':
        return 400
    # elif param_type == '':
    else:
        return None
    
# ========================================================
# Get parameter for data generation

def get_parameter(param_type):

    if param_type == 'amount_of_signals':
        return 1000
    elif param_type == 'signal_length':
        return 4096
    elif param_type == 'good_first_peak_low':
        return 100
    elif param_type == 'good_first_peak_high':
        return 3000
    elif param_type == 'good_second_peak_low':
        return 2000
    elif param_type == 'good_second_peak_high':
        return 3000
    elif param_type == 'good_third_peak_low':
        return 6000
    elif param_type == 'good_third_peak_high':
        return 7000
    elif param_type == 'bad_first_peak_low':
        return 2500
    elif param_type == 'bad_first_peak_high':
        return 3500
    elif param_type == 'bad_second_peak_low':
        return 1500
    elif param_type == 'bad_second_peak_high':
        return 2500
    elif param_type == 'bad_third_peak_low':
        return 7500
    elif param_type == 'bad_third_peak_high':
        return 8500
    elif param_type == 'add_fourth_peak_low':
        return 6000
    elif param_type == 'add_fourth_peak_high':
        return 8000
    elif param_type == 'first_amplitudes_good_low':
        return 85000000
    elif param_type == 'first_amplitudes_good_high':
        return 90000000
    elif param_type == 'second_amplitudes_good_low':
        return 75000000
    elif param_type == 'second_amplitudes_good_high':
        return 80000000
    elif param_type == 'third_amplitudes_good_low':
        return 20000000
    elif param_type == 'third_amplitudes_good_high':
        return 30000000
    elif param_type == 'first_amplitudes_bad_low':
        return 60000000
    elif param_type == 'first_amplitudes_bad_high':
        return 70000000
    elif param_type == 'second_amplitudes_bad_low':
        return 20000000
    elif param_type == 'second_amplitudes_bad_high':
        return 25000000
    elif param_type == 'third_amplitudes_bad_low':
        return 50000000
    elif param_type == 'third_amplitudes_bad_high':
        return 55000000   
    elif param_type == 'fourth_amplitudes_add_low':
        return 45000000
    elif param_type == 'fourth_amplitudes_add_high':
        return 55000000  
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