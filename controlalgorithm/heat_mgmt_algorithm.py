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

# define dictionary to map external temperature vs desired internal temperature and actual internal temperature vs desired internal temperature to tilt angle
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

def get_cloud_cover_percentage():
    # TODO: get cloud coverage in percentage from Internet
    return 80

def get_ext_temp():
    # TODO: get external temperature in Celsius from Internet
    return -10

def get_int_temp():
    # TODO: get internal temperature readings from sensor
    return 20

# formula to determine the weight for cloud cover in the algorithm based on angle of the sun
def get_solar_angle_weight():
    solar_angle = max_sun.get_solar_angle()
    if solar_angle <= 0:
        weight = 0
    else:
        weight = solar_angle / 90
    return weight

def heat_mgmt_algorithm(cc, et, at, w): # TODO: rm args when methods implemented
    # cloud_cover_percentage = get_cloud_cover_percentage() # TODO: actual method
    # ext_temp = get_ext_temp() # TODO: actual method
    # act_int_temp = get_int_temp() # TODO: actual method
    cloud_cover_percentage = cc # TODO: for testing
    ext_temp = et # TODO: for testing
    act_int_temp = at # TODO: for testing
    des_int_temp = 22 #TODO: get this from user input?

    ext_vs_des = temp_to_temp_range(ext_temp - des_int_temp)
    act_int_vs_des_int = temp_to_temp_range(act_int_temp - des_int_temp)
    cloud_cover = cover_percentage_to_cloud_cover(cloud_cover_percentage)

    # solar_angle_weight = get_solar_angle_weight() # TODO: actual method
    solar_angle_weight = w
    temp_weight = 1 - solar_angle_weight

    if ext_vs_des is "equilibrium":
        tilt_angle_cc = 0 # don't care term (but must be real number for calculations)
        solar_angle_weight = 0 # TODO: for testing
        temp_weight = 1
        print("ext vs des is equilibrium. do nothing")
    else:
        tilt_angle_cc = evd_cc_to_tilt_angle(ext_vs_des, cloud_cover)

    if act_int_vs_des_int is "equilibrium":
        tilt_angle_temp = 0 # don't care term (but must be real number for calculations)
        solar_angle_weight = 1
        temp_weight = 0
        print("act int vs des int is equilibrium. do nothing")
    else:
        tilt_angle_temp = evd_avd_to_tilt_angle(ext_vs_des, act_int_vs_des_int)

    if ext_vs_des is "equilibrium" and act_int_vs_des_int is "equilibrium":
        print("all temp differences at equilibrium. no need to change tilt angle")
        return 0 # TODO: don't move the motor

    tilt_angle_final = tilt_angle_cc * solar_angle_weight + tilt_angle_temp * temp_weight

    return tilt_angle_final
    
if __name__ == "__main__":
    result = heat_mgmt_algorithm(80, -10, 20, 0.88) # expect cold, overcast and cold, cool: 51*0.88 + (-20)*0.12 = 42.48
    print(result)