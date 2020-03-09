"""
Date: Mar 6, 2020
Author: Ishaat Chowdhury
Contents: Temperature Sensor Classes
"""

import bme280
import smbus2
from abc import ABCMeta, abstractmethod

""" Base class for any temperature sensor used in system """
class TemperatureSensor(metaclass=ABCMeta):

    """ Check for subclass """
    @classmethod
    def __subclasshook__(cls, subclass):
        return hasattr(subclass, "getSample") and callable(subclass.getSample) or NotImplemented
    
    """Return sample from temperature sensor

    Returns:
        int - temperature sample
    """
    @abstractmethod
    def getSample(self):
        raise NotImplementedError()

""" Mock temperature sensor """
class MockTemperatureSensor(TemperatureSensor):

    """Return sample from temperature sensor

    Returns:
        int - temperature sample
    """
    def getSample(self):
        return 25

""" BME 280 Temperature Sensor """
class BME280TemperatureSensor(TemperatureSensor):

    """ Construct new instance of temperature sensor """
    def __init__(self):
        # Calibration parameters for the temperature sensor (Bosch BME280)
        # i2cdetect -y 1
        # https://pypi.org/project/RPi.bme280/
        # https://www.waveshare.com/wiki/BME280_Environmental_Sensor
        # https://www.waveshare.com/w/upload/7/75/BME280_Environmental_Sensor_User_Manual_EN.pdf
        self.port = 1
        self.tempSensorAddress = 0x76
        self.bus = smbus2.SMBus(self.port)
        self.calibrationParams = bme280.load_calibration_params(self.bus, self.tempSensorAddress)


    """Return sample from temperature sensor

    Returns:
        int - temperature sample
    """
    def getSample(self):
        # take a single reading and return a compensated reading object
        # return temperature from compensated reading
        return bme280.sample(self.bus, self.tempSensorAddress, self.calibrationParams).temperature

    

