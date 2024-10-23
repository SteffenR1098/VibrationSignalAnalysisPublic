# VibrationSignalAnalysisPublic
Showcase repository for vibration signal analysis

Project description - imaginary with simulated data only.

This puplic repository contains the work for a showcase project with the target to analyse vibration data coming from a rotation sensor. The rotation sensor is connected with a FFT modul delivering frequency data to a "gateway" (a mini-PC). On the gateway, a ML modul is encapsulated in a docker container and called AIMonitor. The AIMonitor connects to a SQLite DB to store training data and a trained ML model can also be stored. It is assumed that MTTQ is used to transfer operational commands to the AIMonitor and to recieve results in operational mode.

Since this is a showcase scenario, simulated data (based on a description of real life data) is generated and stored in a separate SQLite DB and made available by a AIProducer modul to simulate the set up with vibration sensor and FFT module. 


The AIMonitor collects the data and stores it in a SQLite DB. The labeling of the data is done with the assumption that it is known if the monitored machine is running well or not at any given point.

The ML modul is then trained with the stored data and afterwards tested with new data to simulate operational mode.

