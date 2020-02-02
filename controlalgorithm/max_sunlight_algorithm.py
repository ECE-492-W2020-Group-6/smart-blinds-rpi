def get_solar_angle():
    # get solar angle from Internet
    return 80

def max_sunlight_algorithm():
    solar_angle = get_solar_angle()
    tilt_angle = -solar_angle
    return tilt_angle
    
if __name__ == "__main__":
    result = max_sunlight_algorithm()
    print(result)