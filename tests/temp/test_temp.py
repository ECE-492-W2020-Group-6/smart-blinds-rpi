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
"""
port = 1
address = 0x76
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
        int_temp = get_int_temp()
        print(int_temp)

if __name__ == "__main__":
    unittest.main()