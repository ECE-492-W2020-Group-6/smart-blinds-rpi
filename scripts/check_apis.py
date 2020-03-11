"""
Date: Mar 9, 2020
Author: Sam Wu
Contents: Perform unit tests for API calls
Location (lat/lon)
Cloud Cover Percentage
External Temp
"""

import datetime
import dotenv
import json
import os
import pandas
import pvlib.solarposition
import requests
import unittest
import sys

import controlalgorithm.persistent_data as persistent_data

"""
Test class for the APIs.
Inherits from the TestCase class
"""
class TestAPI(unittest.TestCase):

    def test_geocoding_api(self):
        persistent_data.get_lat_lon()

    def test_darksky_api(self):
        lat, lon, timezone_adjustment = persistent_data.get_lat_lon()
        persistent_data.update_cloud_cover_percentage_and_ext_temp(lat, lon, timezone_adjustment)

if __name__ == "__main__":
    unittest.main()