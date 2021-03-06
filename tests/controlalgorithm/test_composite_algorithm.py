"""
Date: Mar 7, 2020
Author: Sam Wu
Contents: Unit tests for the Composite Algorithm
for obtaining the optimal tilt angle for both
maximum sunlight for user convenience
and minimum power consumption for energy efficiency
"""

from unittest import TestCase
from unittest.mock import patch

import controlalgorithm.user_defined_exceptions as exceptions
import controlalgorithm.max_sunlight_algorithm as max_sun
import controlalgorithm.heat_mgmt_algorithm as heat_mgmt
import controlalgorithm.composite_algorithm as comp
import controlalgorithm.persistent_data as p_data
from tempsensor.tempsensor import MockTemperatureSensor

"""
Test class for the control algorithm tests.
Inherits from the TestCase class

Methods:
test_comp_normal: Tests the Composite Algorithm for normal input
test_comp_exception: Test for invalid input
"""
class TestControlAlgorithms(TestCase):
    @patch('controlalgorithm.max_sunlight_algorithm.get_solar_angle')
    @patch('controlalgorithm.persistent_data.get_cloud_cover_percentage_and_ext_temp')
    @patch('controlalgorithm.heat_mgmt_algorithm.get_solar_angle_weight')
    def test_comp_normal(self, mock_get_weight, mock_get_cc_et, mock_get_solar_angle):
        mock_get_solar_angle.return_value = 80        
        mock_get_cc_et.return_value = [80, -10]
        mock_get_weight.return_value = 0.88
        self.assertAlmostEqual(comp.composite_algorithm( MockTemperatureSensor() ), -65.3024, places=4)

    @patch('controlalgorithm.max_sunlight_algorithm.get_solar_angle')
    @patch('controlalgorithm.persistent_data.get_cloud_cover_percentage_and_ext_temp')
    @patch('controlalgorithm.heat_mgmt_algorithm.get_solar_angle_weight')
    def test_comp_exception(self, mock_get_weight, mock_get_cc_et, mock_get_solar_angle):
        mock_get_solar_angle.return_value = 810        
        mock_get_cc_et.return_value = [80, -10]
        mock_get_weight.return_value = 0.88
        with self.assertRaises(exceptions.InputError):
            comp.composite_algorithm( MockTemperatureSensor() )

        mock_get_solar_angle.return_value = 10        
        mock_get_cc_et.return_value = [180, -10]
        mock_get_weight.return_value = 0.88
        with self.assertRaises(exceptions.InputError):
            comp.composite_algorithm( MockTemperatureSensor() )

if __name__ == "__main__":
    unittest.main()
