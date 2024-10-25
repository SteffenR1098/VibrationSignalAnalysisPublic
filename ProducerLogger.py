'''
    Class for dummy logger for signal producer.
'''

class ProducerLogger():
    '''
        Dummy logger
    '''
    def __init__(self):
        '''
            Constructor - not needed
        '''
        pass

    def print(self, text):
        '''
            print normal message
        '''
        print('ProducerLogger --- ', text)

    def stateChange(self, text):
        '''
            print message concerning state changes
        '''
        print('ProducerLogger state --- ', text)