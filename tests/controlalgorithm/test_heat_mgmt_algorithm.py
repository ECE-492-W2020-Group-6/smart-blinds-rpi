"""
Date: Mar 7, 2020
Author: Sam Wu
Contents: Unit tests for the Heat Algorithm
for obtaining the optimal tilt angle for minimum power consumption for energy efficiency
"""

import unittest
from unittest.mock import patch

import controlalgorithm.user_defined_exceptions as exceptions
import controlalgorithm.heat_mgmt_algorithm as heat_mgmt
import controlalgorithm.persistent_data as p_data
import tempsensor.tempsensor as temp

"""
Test class for the control algorithm tests.
Inherits from the TestCase class

Methods:
test_heat_mgmt_normal_input: Tests the Heat Algorithm with normal input
test_heat_mgmt_exception: Test for invalid input
test_heat_mgmt_equil: Test for equilibrium condition
"""
class TestControlAlgorithms(unittest.TestCase):
    @patch('persistent_data.get_cloud_cover_percentage_and_ext_temp')
    @patch('tempsensor.getSample')
    @patch('heat_mgmt_algorithm.get_solar_angle_weight')
    def test_max_sun_normal_input(self, mock_get_cc_et, mock_get_sam, mock_get_weight):
        mock_get_cc_et.side_effect = [80, -10]
        mock_get_sam.return_value = 20
        mock_get_weight.return_value = 0.88
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(), 42.48, places=2)

        mock_get_cc_et.side_effect = [80, -10]
        mock_get_sam.return_value = 20
        mock_get_weight.return_value = 0
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(), -20, places=2)

        mock_get_cc_et.side_effect = [80, -10]
        mock_get_sam.return_value = 20
        mock_get_weight.return_value = 1
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(), 51, places=2)

        mock_get_cc_et.side_effect = [87, 22]
        mock_get_sam.return_value = 20
        mock_get_weight.return_value = 0.88
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(), -10, places=2)

        mock_get_cc_et.side_effect = [87, 20]
        mock_get_sam.return_value = 22
        mock_get_weight.return_value = 0.88
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(), 46, places=2)

    @patch('persistent_data.get_cloud_cover_percentage_and_ext_temp')
    @patch('tempsensor.getSample')
    @patch('heat_mgmt_algorithm.get_solar_angle_weight')
    def test_max_sun_exception(self, mock_get_cc_et, mock_get_sam, mock_get_weight):
        mock_get_cc_et.side_effect = [101, 0]
        mock_get_sam.return_value = 23
        mock_get_weight.return_value = 0.5
        with self.assertRaises(exceptions.InputError):
            heat_mgmt.heat_mgmt_algorithm()

    @patch('persistent_data.get_cloud_cover_percentage_and_ext_temp')
    @patch('tempsensor.getSample')
    @patch('heat_mgmt_algorithm.get_solar_angle_weight')
    def test_heat_mgmt_equil(self):
        mock_get_cc_et.side_effect = [87, 22]
        mock_get_sam.return_value = 22
        mock_get_weight.return_value = 0.88
        # in actuality motor should do nothing
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(), 0, places=0)

if __name__ == "__main__":
    unittest.main()