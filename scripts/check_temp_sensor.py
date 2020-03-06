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
import time
import unittest
from blinds.blinds_api import SmartBlindsSystem

"""
Test class for the temp sensor.
Inherits from the TestCase class
"""
class TestControlAlgorithms(unittest.TestCase):

    def test_temp_sensor(self):
        system = SmartBlindsSystem(None, None, None)
        count = 0
        while(count < 60):
            int_temp = system.getTemperature()
            print("Internal Temperature:", int_temp)
            time.sleep(1)
            count = count + 1

if __name__ == "__main__":
    unittest.main()
