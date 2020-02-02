import max_sunlight_algorithm as max_sun
import heat_mgmt_algorithm as heat_mgmt

def composite_algorithm():
    tilt_angle_sunlight = max_sun.max_sunlight_algorithm()
    tilt_angle_heat = heat_mgmt.heat_mgmt_algorithm()

    solar_angle_weight = heat_mgmt.get_solar_angle_weight()
    heat_weight = 1 - solar_angle_weight

    tilt_angle_final = tilt_angle_sunlight * solar_angle_weight + tilt_angle_heat * heat_weight

    return tilt_angle_final

if __name__ == "__main__":
    result = composite_algorithm()
    print(result)