import sys

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

# use dictionary to define a standard for cloud coverage percentages
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
        print("invalid input") #TODO: throw exception?
    return cloud_cover

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

def heat_mgmt_algorithm():
    cloud_cover_percentage = get_cloud_cover_percentage()
    ext_temp = get_ext_temp()
    act_int_temp = get_int_temp()
    des_int_temp = 22 #TODO: get this from user input?

    ext_vs_des = temp_to_temp_range(ext_temp - des_int_temp)
    act_int_vs_des_int = temp_to_temp_range(act_int_temp - des_int_temp)
    cloud_cover = cover_percentage_to_cloud_cover(cloud_cover_percentage)

    solar_angle_weight = get_solar_angle_weight()
    temp_weight = 1 - solar_angle_weight

    if ext_vs_des is "hot" and cloud_cover is "clear":
        tilt_angle_cc = 70
    elif ext_vs_des is "hot" and cloud_cover is "partly cloudy":
        tilt_angle_cc = 65
    elif ext_vs_des is "hot" and cloud_cover is "cloudy":
        tilt_angle_cc = -30
    elif ext_vs_des is "hot" and cloud_cover is "overcast":
        tilt_angle_cc = -25
    elif ext_vs_des is "warm" and cloud_cover is "clear":
        tilt_angle_cc = 65
    elif ext_vs_des is "warm" and cloud_cover is "partly cloudy":
        tilt_angle_cc = 60
    elif ext_vs_des is "warm" and cloud_cover is "cloudy":
        tilt_angle_cc = -35
    elif ext_vs_des is "warm" and cloud_cover is "overcast":
        tilt_angle_cc = -30
    elif ext_vs_des is "cool" and cloud_cover is "clear":
        tilt_angle_cc = -15
    elif ext_vs_des is "cool" and cloud_cover is "partly cloudy":
        tilt_angle_cc = -20
    elif ext_vs_des is "cool" and cloud_cover is "cloudy":
        tilt_angle_cc = 41
    elif ext_vs_des is "cool" and cloud_cover is "overcast":
        tilt_angle_cc = 46
    elif ext_vs_des is "cold" and cloud_cover is "clear":
        tilt_angle_cc = -10
    elif ext_vs_des is "cold" and cloud_cover is "partly cloudy":
        tilt_angle_cc = -15
    elif ext_vs_des is "cold" and cloud_cover is "cloudy":
        tilt_angle_cc = 46
    elif ext_vs_des is "cold" and cloud_cover is "overcast":
        tilt_angle_cc = 51
    else:
        solar_angle_weight = 0
        print("ext vs des is equilibrium. do nothing")
        
    if ext_vs_des is "hot" and act_int_vs_des_int is "hot":
        tilt_angle_temp = 80
    elif ext_vs_des is "hot" and act_int_vs_des_int is "warm":
        tilt_angle_temp = 75
    elif ext_vs_des is "hot" and act_int_vs_des_int is "cool":
        tilt_angle_temp = -5
    elif ext_vs_des is "hot" and act_int_vs_des_int is "cold":
        tilt_angle_temp = 0
    elif ext_vs_des is "warm" and act_int_vs_des_int is "hot":
        tilt_angle_temp = 75
    elif ext_vs_des is "warm" and act_int_vs_des_int is "warm":
        tilt_angle_temp = 70
    elif ext_vs_des is "warm" and act_int_vs_des_int is "cool":
        tilt_angle_temp = -10
    elif ext_vs_des is "warm" and act_int_vs_des_int is "cold":
        tilt_angle_temp = -5
    elif ext_vs_des is "cool" and act_int_vs_des_int is "hot":
        tilt_angle_temp = 70
    elif ext_vs_des is "cool" and act_int_vs_des_int is "warm":
        tilt_angle_temp = 65
    elif ext_vs_des is "cool" and act_int_vs_des_int is "cool":
        tilt_angle_temp = -15
    elif ext_vs_des is "cool" and act_int_vs_des_int is "cold":
        tilt_angle_temp = -10
    elif ext_vs_des is "cold" and act_int_vs_des_int is "hot":
        tilt_angle_temp = 65
    elif ext_vs_des is "cold" and act_int_vs_des_int is "warm":
        tilt_angle_temp = 60
    elif ext_vs_des is "cold" and act_int_vs_des_int is "cool":
        tilt_angle_temp = -20
    elif ext_vs_des is "cold" and act_int_vs_des_int is "cold":
        tilt_angle_temp = -15
    elif ext_vs_des is "equilibrium" and (act_int_vs_des_int is "hot" or act_int_vs_des_int is "warm"):
        tilt_angle_temp = 70
    elif ext_vs_des is "equilibrium" and (act_int_vs_des_int is "cool" or act_int_vs_des_int is "cold"):
        tilt_angle_temp = -10
    else:
        temp_weight = 0
        print("act int vs des int is equilibrium. do nothing")

    tilt_angle_final = tilt_angle_cc * solar_angle_weight + tilt_angle_temp * temp_weight
    return tilt_angle_final
    
if __name__ == "__main__":
    result = heat_mgmt_algorithm()
    print(result)