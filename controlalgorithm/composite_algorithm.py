import max_sunlight_algorithm as max_sun
import heat_mgmt_algorithm as heat_mgmt

def composite_algorithm(angle, cc, et, at , w): # TODO: rm args when methods implemented
    # tilt_angle_sunlight = max_sun.max_sunlight_algorithm() # TODO: actual inputs
    # tilt_angle_heat = heat_mgmt.heat_mgmt_algorithm() # TODO: actual inputs
    tilt_angle_sunlight = max_sun.max_sunlight_algorithm(angle) # TODO: for testing
    tilt_angle_heat = heat_mgmt.heat_mgmt_algorithm(cc, et, at, w) # TODO: for testing

    # solar_angle_weight = heat_mgmt.get_solar_angle_weight() # TODO: actual method
    solar_angle_weight = w # TODO: for testing
    heat_weight = 1 - solar_angle_weight

    tilt_angle_final = tilt_angle_sunlight * solar_angle_weight + tilt_angle_heat * heat_weight

    return tilt_angle_final

if __name__ == "__main__":
    result = composite_algorithm(80, 80, -10, 20, 0.88) # expect -80*0.88 + 42.48*0.12 = -65.3024
    print(result)