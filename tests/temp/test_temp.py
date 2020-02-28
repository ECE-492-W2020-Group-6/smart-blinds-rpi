"""
Date: Feb 28, 2020
Author: Sam Wu
Contents: Unit tests for the temperature sensor BME280
"""

import bme280
import datetime
import dotenv
import os
import requests
import smbus2
import sys
import unittest

"""
Calibration parameters for the temperature sensor (Bosch BME280)
i2cdetect -y 1
https://pypi.org/project/RPi.bme280/
https://www.waveshare.com/wiki/BME280_Environmental_Sensor
https://www.waveshare.com/w/upload/7/75/BME280_Environmental_Sensor_User_Manual_EN.pdf
"""
port = 1
address = 0x77
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

"""
Get the internal temperature from the Bosch BME280 digital sensor module
"""
def get_int_temp():
    # take a single reading and return a compensated_reading object
    data = bme280.sample(bus, address, calibration_params)

    # get the temperature attribute from the compensated_reading class 
    int_temp = data.temperature
    return int_temp

"""
Test class for the temp sensor.
Inherits from the TestCase class
"""
class TestControlAlgorithms(unittest.TestCase):

    def test_temp_sensor(self):
        while(true):
            int_temp = get_int_temp()
            print("Internal Temperature:", int_temp)
            sleep(1)

if __name__ == "__main__":
    unittest.main()