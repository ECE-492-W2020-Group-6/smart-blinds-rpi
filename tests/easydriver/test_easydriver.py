import pytest
from easydriver.easydriver import EasyDriver, MicroStepResolution, StepDirection
from gpiozero import GPIOPinMissing, Device
from gpiozero.pins.mock import MockFactory

# Set the default pin factory to a mock factory
Device.pin_factory = MockFactory()

class TestEasyDriver:
    STEP_PIN = 20
    DIR_PIN = 21
    ENABLE_PIN = 25
    MS1_PIN = 24
    MS2_PIN = 23

    @pytest.fixture()
    def driver(self):
        driver = EasyDriver(step_pin=self.STEP_PIN,
                    dir_pin=self.DIR_PIN, 
                    ms1_pin=self.MS1_PIN, 
                    ms2_pin=self.MS2_PIN,
                    enable_pin=self.ENABLE_PIN)
        yield driver
        driver.close()

    def test_init_no_step_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver()

    def test_init_no_dir_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.STEP_PIN)

    def test_init_no_ms1_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.STEP_PIN, dir_pin=self.DIR_PIN)

    def test_init_no_ms2_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.STEP_PIN, dir_pin=self.DIR_PIN, ms1_pin=self.MS1_PIN)

    def test_init_no_enable_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.STEP_PIN,
                    dir_pin=self.DIR_PIN, 
                    ms1_pin=self.MS1_PIN, 
                    ms2_pin=self.MS2_PIN)

    def test_init_success(self, driver):
        assert driver.ms1_pin.state == 0
        assert driver.ms2_pin.state == 0

    def test_set_microstep_resolution_full_step(self, driver):
        driver.microstep_resolution = MicroStepResolution.FULL_STEP
        assert driver.ms1_pin.state == 0 
        assert driver.ms2_pin.state == 0 

    def test_set_microstep_resolution_half_step(self, driver):
        driver.microstep_resolution = MicroStepResolution.HALF_STEP
        assert driver.ms1_pin.state == 1
        assert driver.ms2_pin.state == 0 

    def test_set_microstep_resolution_quarter_step(self, driver):
        driver.microstep_resolution = MicroStepResolution.QUARTER_STEP
        assert driver.ms1_pin.state == 0
        assert driver.ms2_pin.state == 1 

    def test_set_microstep_resolution_eighth_step(self, driver):
        driver.microstep_resolution = MicroStepResolution.EIGHTH_STEP
        assert driver.ms1_pin.state == 1
        assert driver.ms2_pin.state == 1 

    def test_one_step_forward(self, driver):
        driver.step(1)
        assert driver.dir_pin.state == 0

    def test_one_step_reverse(self, driver):
        driver.step(1, direction=StepDirection.REVERSE)
        assert driver.dir_pin.state == 1

