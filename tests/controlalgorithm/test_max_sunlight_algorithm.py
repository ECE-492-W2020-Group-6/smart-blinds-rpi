"""
Date: Mar 7, 2020
Author: Sam Wu
Contents: Unit test for the Sunlight Algorithm
for obtaining the optimal tilt angle for maximum sunlight for the user's convenience
"""

import sys
sys.path.append('../controlalgorithm')

from unittest import TestCase
from unittest.mock import patch

import controlalgorithm.user_defined_exceptions as exceptions
import controlalgorithm.max_sunlight_algorithm as max_sun

"""
Test class for the control algorithm tests.
Inherits from the TestCase class

Methods:
test_max_sun: Tests the Sunlight Algorithm
"""
class TestMaxSun(TestCase):

    @patch('max_sun.get_solar_angle')
    def test_max_sun_normal_input(self, mock_get_solar_angle):
        mock_get_solar_angle.return_value = 80
        self.assertEqual(max_sun.max_sunlight_algorithm(), -80)

        mock_get_solar_angle.return_value = 0
        self.assertEqual(max_sun.max_sunlight_algorithm(), 0)
    
    @patch('max_sun.get_solar_angle')
    def test_max_sun_edge_input(self, mock_get_solar_angle):
        mock_get_solar_angle.return_value = 90
        self.assertEqual(max_sun.max_sunlight_algorithm(), -90)

        mock_get_solar_angle.return_value = -90
        self.assertEqual(max_sun.max_sunlight_algorithm(), 90)

    @patch('max_sun.get_solar_angle')
    def test_max_sun_exception(self, mock_get_solar_angle):
        mock_get_solar_angle.return_value = -100
        with self.assertRaises(exceptions.InputError):
            max_sun.max_sunlight_algorithm()

if __name__ == "__main__":
    unittest.main()