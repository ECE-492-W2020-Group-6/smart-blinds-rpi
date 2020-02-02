import user_defined_exceptions as exceptions

def get_solar_angle():
    # TODO: get solar angle from Internet
    return 80

def max_sunlight_algorithm(angle): # TODO: rm angle arg when get_solar_angle implemented
    # solar_angle = get_solar_angle() # TODO: actual method
    solar_angle = angle # TODO: for testing
    if (angle > 90 or angle < -90):
        raise exceptions.InputError("get_solar_angle()", "Solar Angle may only be between -90 and 90 degrees inclusive")
    tilt_angle = -solar_angle
    return tilt_angle
    
if __name__ == "__main__":
    result = max_sunlight_algorithm(80) # expect -80
    print(result)