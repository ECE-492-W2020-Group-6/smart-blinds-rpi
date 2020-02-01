import pytest
from easydriver.easydriver import EasyDriver, MicroStepResolution
from gpiozero import GPIOPinMissing, Device
from gpiozero.pins.mock import MockFactory

# Set the default pin factory to a mock factory
Device.pin_factory = MockFactory()

class TestEasyDriver:
    step_pin = 20
    dir_pin = 21
    enable_pin = 25
    ms1_pin = 24
    ms2_pin = 23

    def test_init_no_step_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver()

    def test_init_no_dir_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.step_pin)

    def test_init_no_ms1_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.step_pin, dir_pin=self.dir_pin)

    def test_init_no_ms2_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.step_pin, dir_pin=self.dir_pin, ms1_pin=self.ms1_pin)

    def test_init_no_enable_pin(self):
        with pytest.raises(GPIOPinMissing):
            EasyDriver(step_pin=self.step_pin,
                    dir_pin=self.dir_pin, 
                    ms1_pin=self.ms1_pin, 
                    ms2_pin=self.ms2_pin)

    def test_init_success(self):
        driver = EasyDriver(step_pin=self.step_pin,
                    dir_pin=self.dir_pin, 
                    ms1_pin=self.ms1_pin, 
                    ms2_pin=self.ms2_pin,
                    enable_pin=self.enable_pin)

    def test_set_microstep_resolution_full_step(self):
        driver = EasyDriver(step_pin=self.step_pin,
                    dir_pin=self.dir_pin, 
                    ms1_pin=self.ms1_pin, 
                    ms2_pin=self.ms2_pin,
                    enable_pin=self.enable_pin)

        driver.microstep_resolution = MicroStepResolution.FULL_STEP
        assert driver.ms1_pin.state == 0 and driver.ms2_pin.state == 0 

    # def test_set_microstep_resolution_half_step(self):
    #     driver = EasyDriver(step_pin=self.step_pin,
    #                 dir_pin=self.dir_pin, 
    #                 ms1_pin=self.ms1_pin, 
    #                 ms2_pin=self.ms2_pin,
    #                 enable_pin=self.enable_pin)
    #
    #     driver.microstep_resolution = MicroStepResolution.HALF_STEP
    #     assert driver.ms1_pin.state == 1 and driver.ms2_pin.state == 0 
    #
    # def test_set_microstep_resolution_quarter_step(self):
    #     driver = EasyDriver(step_pin=self.step_pin,
    #                 dir_pin=self.dir_pin, 
    #                 ms1_pin=self.ms1_pin, 
    #                 ms2_pin=self.ms2_pin,
    #                 enable_pin=self.enable_pin)
    #
    #     driver.microstep_resolution = MicroStepResolution.QUARTER_STEP
    #     assert driver.ms1_pin.state == 0 and driver.ms2_pin.state == 1 
    #
    # def test_set_microstep_resolution_eighth_step(self):
    #     driver = EasyDriver(step_pin=self.step_pin,
    #                 dir_pin=self.dir_pin, 
    #                 ms1_pin=self.ms1_pin, 
    #                 ms2_pin=self.ms2_pin,
    #                 enable_pin=self.enable_pin)
    #
    #     driver.microstep_resolution = MicroStepResolution.EIGHTH_STEP
    #     assert driver.ms1_pin.state == 1 and driver.ms2_pin.state == 1 
