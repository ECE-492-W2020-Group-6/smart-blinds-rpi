"""
Date: Feb 26, 2020
Author: Ishaat Chowdhury
Contents: Motor test script
"""

from easydriver.easydriver import EasyDriver, PowerState, MicroStepResolution,  StepDirection
from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero import Device
import time
import RPi.GPIO as rpigpio

if __name__ == "__main__":
    STEP_PIN = 20
    DIR_PIN = 21
    ENABLE_PIN = 25
    MS1_PIN = 24
    MS2_PIN = 23

    rpigpio.setmode(rpigpio.BCM)
    rpigpio.setwarnings(False)

    Device.pin_factory = RPiGPIOFactory()

    driver = EasyDriver(step_pin=STEP_PIN,
                dir_pin=DIR_PIN, 
                ms1_pin=MS1_PIN, 
                ms2_pin=MS2_PIN,
                enable_pin=ENABLE_PIN)

    print("Starting script...")

    while True:
        step_input = input("Number of steps: ")
        steps = int(step_input)

        dir_input = input("Direction [fwd or rev]: ")
        direction = StepDirection.FORWARD if dir_input.lower() in \
                ["fwd", "forward", "f"] else StepDirection.REVERSE

        ms_res_input = input("Microstep Resolution: [full or half or quarter or eighth]: ")
        d = {
            "full": MicroStepResolution.FULL_STEP,
            "1": MicroStepResolution.FULL_STEP,
            "half": MicroStepResolution.HALF_STEP,
            "1/2": MicroStepResolution.HALF_STEP,
            "quarter": MicroStepResolution.QUARTER_STEP,
            "1/4": MicroStepResolution.QUARTER_STEP,
            "eigth": MicroStepResolution.EIGHTH_STEP,
            "1/8": MicroStepResolution.EIGHTH_STEP,
        }
        microstep_resolution = d[ms_res_input]
        
        driver.microstep_resolution = microstep_resolution
        driver.step(steps=steps, direction=direction)
