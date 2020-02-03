"""
Date: Jan 31, 2020
Author: Sam Wu
Contents: Algorithm for obtaining the optimal tilt angle for maximum sunlight for the user's convenience
"""

import user_defined_exceptions as exceptions

"""
Get the solar angle from the Internet
"""
def get_solar_angle():
    return 80

"""
Determine the optimal tilt angle for maximum sunlight for the user's convenience

Inputs:
solar_angle (float): angle of the sun

Output:
tilt_angle (float): angle to tilt the blinds for max sunlight
"""
def max_sunlight_algorithm(angle):
    solar_angle = angle
    if (angle > 90 or angle < -90):
        raise exceptions.InputError("get_solar_angle()", "Solar Angle may only be between -90 and 90 degrees inclusive")
    tilt_angle = -solar_angle
    return tilt_angle
    
if __name__ == "__main__":
    result = max_sunlight_algorithm(80) # expect -80
    print(result)