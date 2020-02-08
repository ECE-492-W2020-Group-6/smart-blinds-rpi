"""
Date: Jan 31, 2020
Author: Ishaat Chowdhury
Contents: Unit tests for Software Driver of SparkFun EasyDriver Board
"""

import pytest
from easydriver.easydriver import EasyDriver, MicroStepResolution, StepDirection
from gpiozero import GPIOPinMissing, Device
from gpiozero.pins.mock import MockFactory

# Set the default pin factory to a mock factory
Device.pin_factory = MockFactory()

"""Class holding unit tests for driver
"""
class TestEasyDriver:
    STEP_PIN = 20
    DIR_PIN = 21
    ENABLE_PIN = 25
    MS1_PIN = 24
    MS2_PIN = 23

    """Creates and returns a fresh instance of a driver for tests.

    Also handles cleanup after the yield.
    
    Yields:
        EasyDriver -- fresh instance of driver for each test
    """
    @pytest.fixture()
    def driver(self):
        driver = EasyDriver(step_pin=self.STEP_PIN,
                    dir_pin=self.DIR_PIN, 
                    ms1_pin=self.MS1_PIN, 
                    ms2_pin=self.MS2_PIN,
                    enable_pin=self.ENABLE_PIN)
        yield driver
        driver.close()

    """Test init with no step pin
    """
    def test_init_no_step_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver()

    """Test init with no dir pin
    """
    def test_init_no_dir_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.STEP_PIN)

    """Test init with no ms1 pin
    """
    def test_init_no_ms1_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.STEP_PIN, dir_pin=self.DIR_PIN)

    """Test init with no ms2 pin
    """
    def test_init_no_ms2_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.STEP_PIN, dir_pin=self.DIR_PIN, ms1_pin=self.MS1_PIN)

    """Test init with no enable pin
    """
    def test_init_no_enable_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.STEP_PIN,
                    dir_pin=self.DIR_PIN, 
                    ms1_pin=self.MS1_PIN, 
                    ms2_pin=self.MS2_PIN)

    """Test init success
    """
    def test_init_success(self, driver):
        assert driver.step_pin.state == 0
        assert driver.dir_pin.state == 0
        assert driver.ms1_pin.state == 0
        assert driver.ms2_pin.state == 0
        assert driver.enable_pin.state == 1

    """Test setting microstep resolution to full step
    """
    def test_set_microstep_resolution_full_step(self, driver):
        driver.microstep_resolution = MicroStepResolution.FULL_STEP
        assert driver.ms1_pin.state == 0 
        assert driver.ms2_pin.state == 0 

    """Test setting microstep resolution to half step
    """
    def test_set_microstep_resolution_half_step(self, driver):
        driver.microstep_resolution = MicroStepResolution.HALF_STEP
        assert driver.ms1_pin.state == 1
        assert driver.ms2_pin.state == 0 

    """Test setting microstep resolution to quarter step
    """
    def test_set_microstep_resolution_quarter_step(self, driver):
        driver.microstep_resolution = MicroStepResolution.QUARTER_STEP
        assert driver.ms1_pin.state == 0
        assert driver.ms2_pin.state == 1 

    """Test setting microstep resolution to eighth step
    """
    def test_set_microstep_resolution_eighth_step(self, driver):
        driver.microstep_resolution = MicroStepResolution.EIGHTH_STEP
        assert driver.ms1_pin.state == 1
        assert driver.ms2_pin.state == 1 

    """Test moving one step forward
    """
    def test_one_step_forward(self, driver):
        driver.step(1)
        assert driver.dir_pin.state == 0
        assert driver.step_pin.state == 0
        assert driver.enable_pin.state == 1

    """Test moving one step backward
    """
    def test_one_step_reverse(self, driver):
        driver.step(1, direction=StepDirection.REVERSE)
        assert driver.dir_pin.state == 1
        assert driver.step_pin.state == 0
        assert driver.enable_pin.state == 1

