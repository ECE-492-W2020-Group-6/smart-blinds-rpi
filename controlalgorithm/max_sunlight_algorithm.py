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

import persistent_data as p_data
import user_defined_exceptions as exceptions

"""
Given a lat/lon, get the solar angle from pvlib.solarposition
"""
def get_solar_angle():
    lat, lon, timezone_adjustment = p_data.get_lat_lon()

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