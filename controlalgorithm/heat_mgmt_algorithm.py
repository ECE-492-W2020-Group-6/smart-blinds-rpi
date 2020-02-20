"""
Date: Jan 31, 2020
Author: Sam Wu
Contents: Algorithm for obtaining the optimal tilt angle for minimum power consumption for energy efficiency
"""

import bme280
import datetime
import dotenv
import os
import requests
import smbus2
import sys

import max_sunlight_algorithm as max_sun
import persistent_data as p_data
import user_defined_exceptions as exceptions

"""
Calibration parameters for the temperature sensor (Bosch BME280)
"""
port = 1
address = 0x76
bus = smbus2.SMBus(port)
calibration_params = bme280.load_calibration_params(bus, address)

"""
API Keys and Endpoints
"""
dotenv.load_dotenv()
DARKSKY_API_KEY = os.getenv("DARKSKY_API_KEY")
DARKSKY_URL = "https://api.darksky.net/forecast/{DARKSKY_API_KEY}/{lat},{lon}"

"""
Define a standard for temperature ranges
in Celsius
"""
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

"""
Define a standard for cloud coverage percentages
ranging from 0% to 100%
"""
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

"""
Define dictionary to map 
external temperature vs desired internal temperature and cloud cover
to tilt angle
"""
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
Define dictionary to map
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

# Convert Fahrenheit to Celsius
def fahrenheit_to_celsius(fahrenheit):
    celsius = (fahrenheit - 32) / 1.8
    return celsius

"""
Given a lat/lon, get the cloud coverage in terms of a percentage from DarkSky
and the external temperature in Celsius from DarkSky
"""
def get_cloud_cover_percentage_and_ext_temp():
    lat, lon, timezone_adjustment = p_data.get_lat_lon()

    # UTC +0 time (7 hours ahead of MST -7) [MST = UTC - 7]
    date_time = datetime.datetime.today()

    DARKSKY_URL = "https://api.darksky.net/forecast/{}/{},{}".format(DARKSKY_API_KEY, lat, lon)
    # print(DARKSKY_URL)
    weather_req = requests.get(url = DARKSKY_URL)
    weather_data = weather_req.json()

    cloud_cover_percentage = weather_data["currently"]["cloudCover"] * 100
    ext_temp_farenheit = weather_data["currently"]["temperature"]
    ext_temp_celsius = fahrenheit_to_celsius(ext_temp_farenheit)
    return cloud_cover_percentage, ext_temp_celsius

# get the internal temperature from the Bosch BME280 digital sensor module
def get_int_temp():
    # take a single reading and return a compensated_reading object
    data = bme280.sample(bus, address, calibration_params)

    # get the temperature attribute from the compensated_reading class 
    int_temp = data.temperature
    return int_temp

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
def heat_mgmt_algorithm(ac_t):
    cloud_cover_percentage, ext_temp = get_cloud_cover_percentage_and_ext_temp()
    act_int_temp = ac_t
    des_int_temp = 22

    ext_vs_des = temp_to_temp_range(ext_temp - des_int_temp)
    act_int_vs_des_int = temp_to_temp_range(act_int_temp - des_int_temp)
    cloud_cover = cover_percentage_to_cloud_cover(cloud_cover_percentage)

    solar_angle_weight = get_solar_angle_weight()
    temp_weight = 1 - solar_angle_weight

    if ext_vs_des == "equilibrium":
        tilt_angle_cc = 0
        solar_angle_weight = 0
        temp_weight = 1
        print("ext vs des is equilibrium. do nothing")
    else:
        tilt_angle_cc = evd_cc_to_tilt_angle(ext_vs_des, cloud_cover)

    if act_int_vs_des_int == "equilibrium":
        tilt_angle_temp = 0
        solar_angle_weight = 1
        temp_weight = 0
        print("act int vs des int is equilibrium. do nothing")
    else:
        tilt_angle_temp = evd_avd_to_tilt_angle(ext_vs_des, act_int_vs_des_int)

    if ext_vs_des == "equilibrium" and act_int_vs_des_int == "equilibrium":
        print("all temp differences at equilibrium. no need to change tilt angle")
        return 0 

    tilt_angle_final = tilt_angle_cc * solar_angle_weight + tilt_angle_temp * temp_weight
    return tilt_angle_final
    
if __name__ == "__main__":
    # result = heat_mgmt_algorithm(80, -10, 20, 0.88) # expect cold, overcast and cold, cool: 51*0.88 + (-20)*0.12 = 42.48
    result = heat_mgmt_algorithm(20)
    print(result)