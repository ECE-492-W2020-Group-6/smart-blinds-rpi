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

    print("full-step fwd")
    driver.microstep_resolution = MicroStepResolution.FULL_STEP
    driver.step(steps=200, direction=StepDirection.FORWARD)

    print("full-step rev")
    driver.step(steps=200, direction=StepDirection.REVERSE)

    print("half-step fwd")
    driver.microstep_resolution = MicroStepResolution.HALF_STEP
    driver.step(steps=200, direction=StepDirection.FORWARD)

    print("half-step reverse")
    driver.step(steps=200, direction=StepDirection.REVERSE)

    print("quarter-step fwd")
    driver.microstep_resolution = MicroStepResolution.QUARTER_STEP
    driver.step(steps=200, direction=StepDirection.FORWARD)

    print("quarter-step reverse")
    driver.step(steps=200, direction=StepDirection.REVERSE)

    print("eigth-step fwd")
    driver.microstep_resolution = MicroStepResolution.EIGHTH_STEP
    driver.step(steps=200, direction=StepDirection.FORWARD)

    print("eigth-step rev")
    driver.microstep_resolution = MicroStepResolution.EIGHTH_STEP
    driver.step(steps=200, direction=StepDirection.REVERSE)

    driver.close()
