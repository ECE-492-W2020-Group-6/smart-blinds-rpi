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

import user_defined_exceptions as exceptions

"""
API Keys and Endpoints
"""
dotenv.load_dotenv()
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json?key={OPENCAGE_API_KEY}&q={place_name}&pretty=1"

"""
Forward Geocoding
Given a location or place name, get the latitude/longitude and time zone of the place
"""
def get_lat_lon():
    # first check if json data file is present and readable
    if os.path.isfile("persistent_data.json") and os.access("persistent_data.json"):
        persistent_data = json.load(persistent_data.json)
        lat = persistent_data_dict["lat"]
        lon = persistent_data_dict["lon"]
        timezone_adjustment = persistent_data_dict["timezone_adjustment"]

    # if not, get the data and create the json file
    else:
        persistent_data_dict = dict()

        place_name = input("Enter location or place name: ")

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
        with open("persistent_data.json", "w") as fp:
            json.dump(persistent_data_dict, fp, indent=4)
    return lat, lon, timezone_adjustment
