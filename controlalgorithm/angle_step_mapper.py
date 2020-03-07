"""
Date: March 6, 2020
Author: Sam Wu
Contents: Map blind slat tilt angle to stepper motor steps and vice-versa
"""

import max_sunlight_algorithm as max_sun
import heat_mgmt_algorithm as heat_mgmt
import composite_algorithm as comp_alg
import persistent_data as p_data
import user_defined_exceptions as exceptions

"""
Class to handle mapping of angle to steps and vice-versa
"""
class AngleStepMapper:
    def __init__( self ):
        pass

    """
    Handles mapping of tilt angle change to stepper motor steps
    For direction, negative tilt angle = CW, positive = CCW
    Inputs:
        tilt_angle (float): the desired blind slat tilt angle
        step_size (float): number of degrees in a full step of the motor
    Output:
        num_steps (int): discrete number of steps
        direction (int): CW = 0, CCW = 1
    """
    def map_angle_to_step(tilt_angle, step_size):
        motor_position = p_data.get_motor_position()
        p_data.set_motor_position(tilt_angle)

        # change in angle = desired tilt angle - motor position
        angle_change = tilt_angle - motor_position

        if angle_change < 0:
            direction = 1
        else:
            direction = 0

        num_steps = angle_change / step_size

        return num_steps, direction

    """
    Handles mapping of stepper motor steps to change in tilt angle
    For direction, negative tilt angle = CW, positive = CCW
    Inputs:
        num_steps (int): discrete number of steps
        direction (int): CW = 0, CCW = 1
        step_size (float): number of degrees in a full step of the motor
    Output:
        tilt_angle (float): the change in blind slat tilt angle
    """
    def map_step_to_angle(num_steps, direction, step_size):
        tilt_angle = num_steps * step_size

        if direction == 1:
            tilt_angle *= -1

        return tilt_angle