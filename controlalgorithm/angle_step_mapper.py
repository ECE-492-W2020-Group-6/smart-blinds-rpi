"""
Date: March 6, 2020
Author: Sam Wu
Contents: Map blind slat tilt angle to stepper motor steps and vice-versa
"""
 
import controlalgorithm.max_sunlight_algorithm as max_sun
import controlalgorithm.heat_mgmt_algorithm as heat_mgmt
import controlalgorithm.composite_algorithm as comp_alg
import controlalgorithm.persistent_data as p_data
import controlalgorithm.user_defined_exceptions as exceptions
from easydriver.easydriver import MicroStepResolution, StepDirection

"""
Constants

ANGLE_POSITION_FACTOR: factor that maps angles to a position in percentage ranging from [-100%, 100%]
NUM_STEPS_FACTOR: factor that is multiplied by the number of steps to get the actual angle, to overcome friction
"""
ANGLE_POSITION_FACTOR = 90 / 100
NUM_STEPS_FACTOR = 1.3

"""
Class to handle mapping of angle to steps and vice-versa
"""
class AngleStepMapper:
    def __init__( self ):
        pass

    """
    Map motor step resolution to angle
    Full step = 1.8 degrees
    """
    def step_resolution_to_angle(self, resolution):
        mapping = {
            MicroStepResolution.FULL_STEP: 1.8,
            MicroStepResolution.HALF_STEP: 0.9,
            MicroStepResolution.QUARTER_STEP: 0.45,
            MicroStepResolution.EIGHTH_STEP: 0.225,
        }
        return mapping[resolution]

    """
    Handles mapping of tilt angle change to stepper motor steps
    For direction, negative tilt angle = CW, positive = CCW
    Inputs:
        tilt_angle (float): the desired blind slat tilt angle
        step_resolution (float): step resolution
    Output:
        num_steps (int): discrete number of steps
        direction (int): FORWARD/CW = 0, REVERSE/CCW = 1 (from easydriver.easydriver StepDirection class)
    """
    def map_angle_to_step(self, tilt_angle, step_resolution):
        motor_position = p_data.get_motor_position()

        # change in angle = desired tilt angle - motor position
        angle_change = tilt_angle - motor_position

        #DEBUG
        print("desired tilt angle: ", tilt_angle, "current motor position: ", motor_position, "change in angle: ", angle_change)

        if angle_change < 0:
            direction = StepDirection.REVERSE
        else:
            direction = StepDirection.FORWARD

        step_size = self.step_resolution_to_angle(step_resolution)
        num_steps = int(abs(round(angle_change / step_size)))

        return num_steps, direction

    """
    Handles mapping of stepper motor steps to change in tilt angle
    For direction, negative tilt angle = CW, positive = CCW
    Inputs:
        num_steps (int): discrete number of steps
        direction (int): CW = 0, CCW = 1 (from easydriver.easydriver StepDirection class)
        step_resolution (float): step resolution
    Output:
        tilt_angle (float): the change in blind slat tilt angle
    """
    def map_step_to_angle(self, num_steps, direction, step_resolution):
        step_size = self.step_resolution_to_angle(step_resolution)
        tilt_angle = num_steps * step_size

        if direction == 1:
            tilt_angle *= -1

        return tilt_angle
