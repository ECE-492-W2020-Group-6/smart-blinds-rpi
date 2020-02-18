"""
Date: Jan 31, 2020
Author: Sam Wu
Contents: Algorithm for obtaining the optimal tilt angle for maximum sunlight for the user's convenience
"""

import dotenv
import os
import requests

import user_defined_exceptions as exceptions

"""
API Keys and Endpoints
SunCalc Reference: https://www.torsten-hoffmann.de/apis/suncalcmooncalc/link_en.html
"""
dotenv.load_dotenv()
OPENCAGE_API_KEY = os.getenv("OPENCAGE_API_KEY")
OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json?key={OPENCAGE_API_KEY}&q={place_name}&pretty=1&no_annotations=1"
SUNCALC_URL = "https://www.suncalc.org/#/{lat},{lon},10/{date}/{time}/1/0"

"""
Get the solar angle from the Internet
"""
def get_solar_angle():
    place_name = input("Enter place name: ")

    OPENCAGE_URL = "https://api.opencagedata.com/geocode/v1/json?key={}&q={}&pretty=1&no_annotations=1".format(OPENCAGE_API_KEY, place_name)
    req = requests.get(url = OPENCAGE_URL)
    data = req.json()

    latitude = data["results"][0]["geometry"]["lat"]
    longitude = data["results"][0]["geometry"]["lng"]

    print("lat: ", latitude)
    print("lon: ", longitude)

    return 80

"""
Determine the optimal tilt angle for maximum sunlight for the user's convenience

Inputs:
solar_angle (float): angle of the sun

Output:
tilt_angle (float): angle to tilt the blinds for max sunlight
"""
def max_sunlight_algorithm(angle):
    solar_angle = get_solar_angle()
    
    solar_angle = angle
    
    if (angle > 90 or angle < -90):
        raise exceptions.InputError("get_solar_angle()", "Solar Angle may only be between -90 and 90 degrees inclusive")
    tilt_angle = -solar_angle
    return tilt_angle
    
if __name__ == "__main__":
    result = max_sunlight_algorithm(80) # expect -80
    print(result)