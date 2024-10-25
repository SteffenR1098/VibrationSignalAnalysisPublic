'''
    Class to act as dummy logger for AISignalMonitor with simple "print" statements.
'''
class AImonitorLogger():
    '''
        Logger class for AISignalMonitor
    '''
    def __init__(self):
        '''
            constructor - not needed
        '''
        pass

    def print(self, text):
        '''
            print normal message
        '''
        print('AImonitorLogger --- ', text)

    def stateChange(self, text):
        '''
            print message concerning state change
        '''
        print('AImonitorLogger state --- ', text)

    def printEval(self, text):
        '''
            print message concerning classification result in operational mode
        '''
        print('AImonitorLogger eval --- ', text)      

