"""
Date: Feb 20, 2020
Author: Sam Wu
Contents: Store persistent data from API calls
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
import sys

import controlalgorithm.user_defined_exceptions as exceptions

"""
Path pointing to the directory where the persistent_data json file is read/written
For main program, will be smart-blinds-rpi folder
For tests, will be tests folder
"""
# persistent_data_path = os.path.join(os.path.dirname(__file__), "..")
persistent_data_path = os.path.dirname(os.path.abspath( __file__ ))
persistent_data_file = os.path.join(persistent_data_path, "..", "persistent_data.json")

"""
API Keys and Endpoints
"""
dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..", ".env")
dotenv.load_dotenv(dotenv_path)

OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json?key={OPENCAGE_API_KEY}&q={place_name}&pretty=1"

DARKSKY_API_KEY = os.getenv("DARKSKY_API_KEY")
DARKSKY_URL = "https://api.darksky.net/forecast/{DARKSKY_API_KEY}/{lat},{lon}"

"""
Forward Geocoding
Given a location or place name, 
get the latitude/longitude
and time zone of the place
Then put the values in persistent_data json file
"""
def get_lat_lon():
    # first check if json data file is present and readable
    if os.path.isfile(persistent_data_file) and os.access(persistent_data_file, os.R_OK):
        with open(persistent_data_file, "r+") as fp:
            persistent_data_dict = json.load(fp)
        lat = persistent_data_dict["lat"]
        lon = persistent_data_dict["lon"]
        timezone_adjustment = persistent_data_dict["timezone_adjustment"]

    # if not, get the data and create the json file
    else:
        persistent_data_dict = dict()

        # place_name = input("Enter location or place name: ")
        place_name = "Edmonton AB"

        OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json?key={}&q={}&pretty=1".format(OPENCAGE_API_KEY, place_name)
        # print(OPENCAGE_URL)
        loc_req = requests.get(url = OPENCAGE_URL)
        geodata = loc_req.json()

        lat = geodata["results"][0]["geometry"]["lat"]
        lon = geodata["results"][0]["geometry"]["lng"]
        timezone_adjustment = geodata["results"][0]["annotations"]["timezone"]["offset_sec"] // 3600 # timezone difference in hours

        persistent_data_dict["lat"] = lat
        persistent_data_dict["lon"] = lon
        persistent_data_dict["timezone_adjustment"] = timezone_adjustment
        
        # save data as json file
        with open(persistent_data_file, "w") as fp:
            json.dump(persistent_data_dict, fp, indent=4)
    return lat, lon, timezone_adjustment

# Convert Fahrenheit to Celsius
def fahrenheit_to_celsius(fahrenheit):
    celsius = (fahrenheit - 32) / 1.8
    return celsius

"""
Given a lat/lon and timezone_adjustment factor,
get the cloud coverage in terms of a percentage from DarkSky
and the external temperature in Celsius from DarkSky
Then put the values in persistent_data json file
"""
def update_cloud_cover_percentage_and_ext_temp(lat, lon, timezone_adjustment):
    with open(persistent_data_file, "r+") as fp:
        persistent_data_dict = json.load(fp)
        
    # UTC +0 time (7 hours ahead of MST -7) [MST = UTC - 7]
    date_time = datetime.datetime.today()

    DARKSKY_URL = "https://api.darksky.net/forecast/{}/{},{}".format(DARKSKY_API_KEY, lat, lon)
    # print(DARKSKY_URL)
    weather_req = requests.get(url = DARKSKY_URL)
    weather_data = weather_req.json()

    cloud_cover_percentage = weather_data["currently"]["cloudCover"] * 100
    ext_temp_farenheit = weather_data["currently"]["temperature"]
    ext_temp_celsius = fahrenheit_to_celsius(ext_temp_farenheit)

    persistent_data_dict["minute"] = date_time.minute # for timestamp/polling purposes
    persistent_data_dict["cloud_cover_percentage"] = cloud_cover_percentage
    persistent_data_dict["ext_temp_celsius"] = ext_temp_celsius

    with open(persistent_data_file, "w") as fp:
        json.dump(persistent_data_dict, fp, indent=4)
    return cloud_cover_percentage, ext_temp_celsius

"""
Get the cloud coverage in terms of a percentage
and the external temperature in Celsius
from persistent_data json file
"""
def get_cloud_cover_percentage_and_ext_temp():
    lat, lon, timezone_adjustment = get_lat_lon()

    with open(persistent_data_file, "r+") as fp:
        persistent_data_dict = json.load(fp)

    # if persistent_data already has cloud cover and ext temp values
    if "minute" in persistent_data_dict:
        # if it has been 10 minutes, do an update of the values
        if persistent_data_dict["minute"] % 10 == 0:
            cloud_cover_percentage, ext_temp_celsius = update_cloud_cover_percentage_and_ext_temp(lat, lon, timezone_adjustment)    

        # otherwise just get the existing values
        else:
            cloud_cover_percentage = persistent_data_dict["cloud_cover_percentage"]
            ext_temp_celsius = persistent_data_dict["ext_temp_celsius"]

    # otherwise cloud cover and ext temp values not in persistent_data
    else:
        cloud_cover_percentage, ext_temp_celsius = update_cloud_cover_percentage_and_ext_temp(lat, lon, timezone_adjustment)    
    return cloud_cover_percentage, ext_temp_celsius

"""
Read and return the motor position (constrained from -90 to 90 in degrees)
"""
def get_motor_position():
    with open(persistent_data_file, "r+") as fp:
        persistent_data_dict = json.load(fp)

    if "motor_position" not in persistent_data_dict:
        persistent_data_dict["motor_position"] = 0
    
    return persistent_data_dict["motor_position"]
    
"""
Update the motor position (constrained from -90 to 90 in degrees)
"""
def set_motor_position(angle):
    with open(persistent_data_file, "r+") as fp:
        persistent_data_dict = json.load(fp)

    persistent_data_dict["motor_position"] = angle

    with open(persistent_data_file, "w") as fp:
        json.dump(persistent_data_dict, fp, indent=4)
    
    return persistent_data_dict["motor_position"]
    