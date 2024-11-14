# VibrationSignalAnalysisPublic
Showcase repository for vibration signal analysis with EdgeAI 

Project description - with simulated data only.

This puplic repository contains the work for a demo case project with the target to analyse vibration data coming from a rotation sensor and is meant as a simplified show case. The rotation sensor is connected with a FFT module delivering frequency data to a "gateway" (a mini-PC). On the gateway, a ML application was created as a Python class and named AISignalMonitor to be encapsulated in a docker container. The AISignalMonitor includes a SQLite DB to store training data and the trained ML model can also be stored as a file and loaded for operational mode. In addition, a simple logger class (AImonitorLogger) is used for communication and just implemented with "print" statements for demonstration.

Since this is a showcase scenario, simulated data (based on a description of real life data) is generated and stored in a separate SQLite DB and made available by a AISignalProducer class to simulate the set up with vibration sensor and FFT module. A second logger class (ProducerLogger) is used to monitor the behaviour of the AISignalProducer. This show case is just a demonstration and does not include the deployment in a docker container or a data connection with mqtt to a real gateway.

In order to show a simulated scenario, a Python script called "run_AISignalMonitor.py" is provided and can be used to show the AISignalMonitor in action with collecting data, training the ML model and operational mode with classification results of the incoming signal data "simulated" by the AISignalProducer.

The showcase also includes the generation of the SQLite DBs and tables and the generation of the simulated signal data. There are three different kinds of signal data. The first class represents a normal state called "good" and the second class represents a critical state called "bad". In addition, a third class (called "additional") is used to simulate a slight variation of the normal state indicating an arising problem in a predictive maintenance scenario. 

Also, this repository does not contain a project that is developed from scratch but a showcase created from a larger demo project for a real customer. For details of the development steps, please see DevelopmentDocumentation.txt.

For the python environment used to create this showcase, please see Requirements.txt.

For more details and the simulated execution with the "run_AISignalMonitor.py" script, please see OverviewAndDetails.pdf.

Remark: The complete source code is self developed and does not fall under any other license than the MIT license added here. 