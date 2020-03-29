"""
Date: March 6, 2020
Author: Sam Wu
Contents: Map blind slat tilt angle to stepper motor steps and vice-versa
"""

from easydriver.easydriver import StepDirection
import controlalgorithm.max_sunlight_algorithm as max_sun
import controlalgorithm.heat_mgmt_algorithm as heat_mgmt
import controlalgorithm.composite_algorithm as comp_alg
import controlalgorithm.persistent_data as p_data
import controlalgorithm.user_defined_exceptions as exceptions

"""
Constants

ANGLE_POSITION_FACTOR: factor that maps angles to a position in percentage ranging from [-100%, 100%]
"""
ANGLE_POSITION_FACTOR = 90 / 100

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
        direction (int): CW = 0, CCW = 1 (from easydriver.easydriver StepDirection class)
    """
    def map_angle_to_step(self, tilt_angle, step_size):
        motor_position = p_data.get_motor_position()
        p_data.set_motor_position(tilt_angle)

        # change in angle = desired tilt angle - motor position
        angle_change = tilt_angle - motor_position

        if angle_change < 0:
            direction = StepDirection.REVERSE
        else:
            direction = StepDirection.FORWARD

        num_steps = angle_change / step_size

        return num_steps, direction

    """
    Handles mapping of stepper motor steps to change in tilt angle
    For direction, negative tilt angle = CW, positive = CCW
    Inputs:
        num_steps (int): discrete number of steps
        direction (int): CW = 0, CCW = 1 (from easydriver.easydriver StepDirection class)
        step_size (float): number of degrees in a full step of the motor
    Output:
        tilt_angle (float): the change in blind slat tilt angle
    """
    def map_step_to_angle(self, num_steps, direction, step_size):
        tilt_angle = num_steps * step_size

        if direction == 1:
            tilt_angle *= -1

        return tilt_angle