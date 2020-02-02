import unittest

import user_defined_exceptions as exceptions
import max_sunlight_algorithm as max_sun
import heat_mgmt_algorithm as heat_mgmt
import composite_algorithm as comp

class TestControlAlgorithms(unittest.TestCase):

    def test_max_sun(self):
        self.assertEqual(max_sun.max_sunlight_algorithm(80), -80)
        self.assertEqual(max_sun.max_sunlight_algorithm(0), 0)
        self.assertEqual(max_sun.max_sunlight_algorithm(90), -90)
        self.assertEqual(max_sun.max_sunlight_algorithm(-90), 90)
        with self.assertRaises(exceptions.InputError):
            max_sun.max_sunlight_algorithm(100)

    def test_heat_mgmt(self):
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(80, -10, 20, 0.88), 42.48, places=2)
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(80, -10, 20, 0), -20, places=0)
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(80, -10, 20, 1), 51, places=0)
        with self.assertRaises(exceptions.InputError):
            heat_mgmt.heat_mgmt_algorithm(101, 0, 23, 0.5)
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(87, 22, 20, 0.88), -10, places=0)
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(87, 20, 22, 0.88), 46, places=0)
        self.assertAlmostEqual(heat_mgmt.heat_mgmt_algorithm(87, 22, 22, 0.88), 0, places=0) # in actuality motor should do nothing

    def test_comp(self):
        self.assertAlmostEqual(comp.composite_algorithm(80, 80, -10, 20, 0.88), -65.3024, places=4)
        with self.assertRaises(exceptions.InputError):
            comp.composite_algorithm(810, 80, -10, 20, 0.88)
        with self.assertRaises(exceptions.InputError):
            comp.composite_algorithm(10, 180, -10, 20, 0.88)

if __name__ == "__main__":
    unittest.main()