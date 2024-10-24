class ProducerLogger():

    def __init__(self):
        pass

    def print(self, text):
        print('ProducerLogger --- ', text)

    def stateChange(self, text):
        print('ProducerLogger state --- ', text)