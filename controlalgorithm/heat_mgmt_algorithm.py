"""
Date: Jan 31, 2020
Author: Sam Wu
Contents: Algorithm for obtaining the optimal tilt angle for minimum power consumption for energy efficiency
"""

import dotenv
import os
import sys

import user_defined_exceptions as exceptions
import max_sunlight_algorithm as max_sun

# define a standard for temperature ranges
def temp_to_temp_range(temp):
    if temp >= 6:
        temp_range = "hot"
    elif temp > 0 and temp < 6:
        temp_range = "warm"
    elif temp > -6 and temp < 0:
        temp_range = "cool"
    elif temp <= -6:
        temp_range = "cold"
    else:
        temp_range = "equilibrium" #algorithm should do nothing
    return temp_range

# define a standard for cloud coverage percentages
def cover_percentage_to_cloud_cover(cloud_cover_percentage):
    if cloud_cover_percentage >= 0 and cloud_cover_percentage < 25:
        cloud_cover = "clear"
    elif cloud_cover_percentage >= 25 and cloud_cover_percentage < 50:
        cloud_cover = "partly cloudy"
    elif cloud_cover_percentage >= 50 and cloud_cover_percentage < 75:
        cloud_cover = "cloudy"
    elif cloud_cover_percentage >= 75 and cloud_cover_percentage < 100:
        cloud_cover = "overcast"
    else:
        raise exceptions.InputError("cover_percentage_to_cloud_cover()", "Cloud Cover Percentage must be between 0 and 100 percent inclusive")
    return cloud_cover

# define dictionary to map external temperature vs desired internal temperature and cloud cover to tilt angle
def evd_cc_to_tilt_angle(evd, cc):
    mapping = {
        ("hot", "clear"): 70,
        ("hot", "partly cloudy"): 65,
        ("hot", "cloudy"): -30,
        ("hot", "overcast"): -25,
        ("warm", "clear"): 65,
        ("warm", "partly cloudy"): 60,
        ("warm", "cloudy"): -35,
        ("warm", "overcast"): -30,
        ("cool", "clear"): -15,
        ("cool", "partly cloudy"): -20,
        ("cool", "cloudy"): 41,
        ("cool", "overcast"): 46,
        ("cold", "clear"): -10,
        ("cold", "partly cloudy"): -15,
        ("cold", "cloudy"): 46,
        ("cold", "overcast"): 51,
    }
    return mapping[evd, cc]

"""
define dictionary to map
external temperature vs desired internal temperature
and actual internal temperature vs desired internal temperature 
to tilt angle
"""
def evd_avd_to_tilt_angle(evd, avd):
    mapping = {
        ("hot", "hot"): 80,
        ("hot", "warm"): 75,
        ("hot", "cool"): -5,
        ("hot", "cold"): 0,
        ("warm", "hot"): 75,
        ("warm", "warm"): 70,
        ("warm", "cool"): -10,
        ("warm", "cold"): 0,
        ("cool", "hot"): 70,
        ("cool", "warm"): 65,
        ("cool", "cool"): -15,
        ("cool", "cold"): -10,
        ("cold", "hot"): 65,
        ("cold", "warm"): 60,
        ("cold", "cool"): -20,
        ("cold", "cold"): -15,
        ("equilibrium", "hot"): 70,
        ("equilibrium", "warm"): 70,
        ("equilibrium", "cool"): -10,
        ("equilibrium", "cold"): -10,
    }
    return mapping[evd, avd]

# get the cloud coverage in terms of a percentage
def get_cloud_cover_percentage():
    return 80

# get the external temperature
def get_ext_temp():
    return -10

# get the internal temperature
def get_int_temp():
    return 20

# formula to determine the weight for cloud cover in the algorithm based on angle of the sun
def get_solar_angle_weight():
    solar_angle = max_sun.get_solar_angle()
    if solar_angle <= 0:
        weight = 0
    else:
        weight = solar_angle / 90
    return weight

"""
Determine the optimal tilt angle for minimum power consumption for energy efficiency

Inputs:
cloud_cover (int): cloud coverage in percentage
ext_temp (float): external temperature
act_int_temp (float): actual internal temperature
solar_weight (float): weighting for the tilt angle determined by the cloud coverage

Output:
tilt_angle_final (float): final tilt angle for maximum energy efficiency
"""
def heat_mgmt_algorithm(cloud_c, ex_t, ac_t, solar_w):
    cloud_cover_percentage = cloud_c
    ext_temp = ex_t
    act_int_temp = ac_t
    des_int_temp = 22

    ext_vs_des = temp_to_temp_range(ext_temp - des_int_temp)
    act_int_vs_des_int = temp_to_temp_range(act_int_temp - des_int_temp)
    cloud_cover = cover_percentage_to_cloud_cover(cloud_cover_percentage)

    solar_angle_weight = solar_w
    temp_weight = 1 - solar_angle_weight

    if ext_vs_des is "equilibrium":
        tilt_angle_cc = 0
        solar_angle_weight = 0
        temp_weight = 1
        print("ext vs des is equilibrium. do nothing")
    else:
        tilt_angle_cc = evd_cc_to_tilt_angle(ext_vs_des, cloud_cover)

    if act_int_vs_des_int is "equilibrium":
        tilt_angle_temp = 0 
        solar_angle_weight = 1
        temp_weight = 0
        print("act int vs des int is equilibrium. do nothing")
    else:
        tilt_angle_temp = evd_avd_to_tilt_angle(ext_vs_des, act_int_vs_des_int)

    if ext_vs_des is "equilibrium" and act_int_vs_des_int is "equilibrium":
        print("all temp differences at equilibrium. no need to change tilt angle")
        return 0 

    tilt_angle_final = tilt_angle_cc * solar_angle_weight + tilt_angle_temp * temp_weight

    return tilt_angle_final
    
if __name__ == "__main__":
    result = heat_mgmt_algorithm(80, -10, 20, 0.88) # expect cold, overcast and cold, cool: 51*0.88 + (-20)*0.12 = 42.48
    print(result)