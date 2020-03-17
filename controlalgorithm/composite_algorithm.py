"""
Date: Jan 31, 2020
Author: Sam Wu
Contents: Composite algorithm for obtaining the optimal tilt angle for both
maximum sunlight for user convenience
and minimum power consumption for energy efficiency
"""

import controlalgorithm.max_sunlight_algorithm as max_sun
import controlalgorithm.heat_mgmt_algorithm as heat_mgmt

"""
Composite algorithm that uses the max_sunlight_algorithm and heat_mgmt_algorithm
together to obtain an optimal balance between sunlight for the user's convenience
and reduction of power consumption for power efficiency

Variables used in tilt angle calculation:
solar_angle (float): angle of the sun
cloud_cover (float): cloud coverage in percentage
ext_temp (float): external temperature in Celsius
act_int_temp (float): actual internal temperature in Celsius
solar_weight (float): weighting for the tilt angle determined by the max sunlight algorithm

Inputs:
tempsensor (TemperatureSensor): an object that handles the internal temp measurement for act_int_temp

Output:
tilt_angle_final (float): final tilt angle for maximum convenience and efficiency
"""
def composite_algorithm(tempsensor):
    tilt_angle_sunlight = max_sun.max_sunlight_algorithm() 
    tilt_angle_heat = heat_mgmt.heat_mgmt_algorithm(tempsensor) 

    solar_angle_weight = heat_mgmt.get_solar_angle_weight()
    heat_weight = 1 - solar_angle_weight

    tilt_angle_final = tilt_angle_sunlight * solar_angle_weight + tilt_angle_heat * heat_weight
    return tilt_angle_final

if __name__ == "__main__":
    # result = composite_algorithm(80, 80, -10, 20, 0.88) # expect -80*0.88 + 42.48*0.12 = -65.3024
    result = composite_algorithm()
    print(result)