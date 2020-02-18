"""
Date: Jan 31, 2020
Author: Sam Wu
Contents: Algorithm for obtaining the optimal tilt angle for maximum sunlight for the user's convenience
"""

import datetime
import dotenv
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
Given a location, get the latitude/longitude, time, and time zone
Use the lat/lon to then get the solar angle from pvlib.solarposition
"""
def get_solar_angle():
    place_name = input("Enter place name: ")

    OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json?key={}&q={}&pretty=1".format(OPENCAGE_API_KEY, place_name)
    print(OPENCAGE_URL)
    loc_req = requests.get(url = OPENCAGE_URL)
    geodata = loc_req.json()

    lat = geodata["results"][0]["geometry"]["lat"]
    lon = geodata["results"][0]["geometry"]["lng"]

    timezone_adjustment = geodata["results"][0]["annotations"]["timezone"]["offset_sec"] // 3600 # timezone difference in hours

    # UTC +0 time (7 hours ahead of MST -7) [MST = UTC - 7]
    date_time = datetime.datetime.today()

    # create data frame for date
    date_data_frame = pandas.DataFrame({
        "year": [date_time.year],
        "month": [date_time.month],
        "day": [date_time.day],
        "hour": [date_time.hour + timezone_adjustment],
        "minute": [date_time.minute]
    })

    # returns datetime objects
    date_data_frame['Timestamp'] = date_data_frame.apply(lambda row: datetime.datetime(row.year, row.month, row.day, row.hour), axis=1)

    # convert to pandas timestamps
    date_data_frame['Timestamp'] = pandas.to_datetime(date_data_frame.Timestamp)

    # create a DatetimeIndex and assign it to the DataFrame
    date_data_frame.index = pandas.DatetimeIndex(date_data_frame.Timestamp)

    # get solar position data as a DataFrame
    solar_position = pvlib.solarposition.get_solarposition(date_data_frame.index, lat, lon)

    # get the apparent elevation of the sun from solar position
    solar_angle = solar_position.iloc[0]['apparent_elevation']
    
    return solar_angle

"""
Determine the optimal tilt angle for maximum sunlight for the user's convenience

Inputs:
solar_angle (float): angle of the sun

Output:
tilt_angle (float): angle to tilt the blinds for max sunlight
"""
def max_sunlight_algorithm():
    solar_angle = get_solar_angle()
    
    if (solar_angle > 90 or solar_angle < -90):
        raise exceptions.InputError("get_solar_angle()", "Solar Angle may only be between -90 and 90 degrees inclusive")
    tilt_angle = -solar_angle
    return tilt_angle
    
if __name__ == "__main__":
    result = max_sunlight_algorithm()
    print(result)