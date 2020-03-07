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
import tempsensor.tempsensor as temp

"""
Test class for the control algorithm tests.
Inherits from the TestCase class

Methods:
test_comp_normal: Tests the Composite Algorithm for normal input
test_comp_exception: Test for invalid input
"""
class TestControlAlgorithms(TestCase):
    @patch('max_sunlight_algorithm.get_solar_angle')
    @patch('persistent_data.get_cloud_cover_percentage_and_ext_temp')
    @patch('tempsensor.getSample')
    @patch('heat_mgmt_algorithm.get_solar_angle_weight')
    def test_comp_normal(self, mock_get_solar_angle, mock_get_cc_et, mock_get_sam, mock_get_weight):
        mock_get_solar_angle = 80        
        mock_get_cc_et.side_effect = [80, -10]
        mock_get_sam.return_value = 20
        mock_get_weight.return_value = 0.88
        self.assertAlmostEqual(comp.composite_algorithm(), -65.3024, places=4)

    @patch('max_sunlight_algorithm.get_solar_angle')
    @patch('persistent_data.get_cloud_cover_percentage_and_ext_temp')
    @patch('tempsensor.getSample')
    @patch('heat_mgmt_algorithm.get_solar_angle_weight')
    def test_comp_exception(self, mock_get_solar_angle, mock_get_cc_et, mock_get_sam, mock_get_weight):
        mock_get_solar_angle = 810        
        mock_get_cc_et.side_effect = [80, -10]
        mock_get_sam.return_value = 20
        mock_get_weight.return_value = 0.88
        with self.assertRaises(exceptions.InputError):
            comp.composite_algorithm(810, 80, -10, 20, 0.88)

        mock_get_solar_angle = 10        
        mock_get_cc_et.side_effect = [180, -10]
        mock_get_sam.return_value = 20
        mock_get_weight.return_value = 0.88
        with self.assertRaises(exceptions.InputError):
            comp.composite_algorithm(10, 180, -10, 20, 0.88)

if __name__ == "__main__":
    unittest.main()