# VibrationSignalAnalysisPublic
Showcase repository for vibration signal analysis with EdgeAI 

Project description - with simulated data only.

This puplic repository contains the work for a showcase project with the target to analyse vibration data coming from a rotation sensor. The rotation sensor is connected with a FFT module delivering frequency data to a "gateway" (a mini-PC). On the gateway, a ML application was created as a Python class and named AISignalMonitor to be encapsulated in a docker container. The AISignalMonitor includes a SQLite DB to store training data and the trained ML model can also be stored as a file and loaded for operational mode. In addition, a logger class (AImonitorLogger) is used for communication and just implemented with "print" statements for demonstration

Since this is a showcase scenario, simulated data (based on a description of real life data) is generated and stored in a separate SQLite DB and made available by a AISignalProducer class to simulate the set up with vibration sensor and FFT module. A second logger class (ProducerLogger) is used to monitor the behaviour of the AISignalProducer.

In order to show a simulated scenario, a Python script called "run_AISignalMonitor.py" is used to show the AISignalMonitor in action with collecting data, training the ML model and operational mode with classification results of the incoming signal data.

The showcase also includes the generation of the SQLite DBs and tables and the generation of the simulated signal data. There are three different kinds of signal data. The first class represents a normal state called "good" and the second class represents a critical state called "bad". In addition, a third class (called "additional") is used to simulate a slight variation of the normal state indicating an arising problem in a predictive maintenance scenario. 