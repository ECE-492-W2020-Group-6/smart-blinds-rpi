from gpiozero import Device, GPIOPinMissing
from enum import IntEnum

class MicroStepResolution(IntEnum):
    FULL_STEP = 0
    HALF_STEP = 1
    QUARTER_STEP = 2
    EIGHTH_STEP = 3

class EasyDriver(Device):
    def __init__(self,
            step_pin=None, 
            dir_pin=None, 
            ms1_pin=None, 
            ms2_pin=None, 
            enable_pin=None, 
            microstep_resolution=MicroStepResolution.FULL_STEP, **kwargs):
        super().__init__(**kwargs)

        self._step_pin = None
        self._dir_pin = None
        self._ms1_pin = None
        self._ms2_pin = None
        self._enable_pin = None

        if step_pin is None:
            raise GPIOPinMissing("No Step Pin Given")

        if dir_pin is None:
            raise GPIOPinMissing("No Dir Pin Given")

        if ms1_pin is None:
            raise GPIOPinMissing("No MS1 Pin Given")
        
        if ms2_pin is None:
            raise GPIOPinMissing("No MS2 Pin Given")
        
        if enable_pin is None:
            raise GPIOPinMissing("No Enable Pin Given")

        self.pin_factory.reserve_pins(self, step_pin)
        self._step_pin = self.pin_factory.pin(step_pin)
        self._step_pin.output_with_state(0)
        
        self.pin_factory.reserve_pins(self, dir_pin)
        self._dir_pin = self.pin_factory.pin(dir_pin)
        self._dir_pin.output_with_state(0)

        self.pin_factory.reserve_pins(self, ms1_pin)
        self._ms1_pin = self.pin_factory.pin(ms1_pin)
        self.ms1_pin.output_with_state(0)
        
        self.pin_factory.reserve_pins(self, ms2_pin)
        self._ms2_pin = self.pin_factory.pin(ms2_pin)
        self.ms2_pin.output_with_state(0)

        self.pin_factory.reserve_pins(self, enable_pin)
        self._enable_pin = self.pin_factory.pin(enable_pin)
        self._enable_pin.output_with_state(1)

        self._microstep_resolution = microstep_resolution

    @property
    def ms1_pin(self):
        return self._ms1_pin

    @property
    def ms2_pin(self):
        return self._ms2_pin

    @property
    def microstep_resolution(self):
        return self._microstep_resolution 

    @microstep_resolution.setter
    def microstep_resolution(self, microstep_resolution):
        self._microstep_resolution = microstep_resolution

        if self._microstep_resolution == MicroStepResolution.FULL_STEP:
            self._ms1_pin.state = 0
            self._ms2_pin.state = 0
        elif self._microstep_resolution == MicroStepResolution.HALF_STEP:
            self._ms1_pin.state = 1
            self._ms2_pin.state = 0
        elif self._microstep_resolution == MicroStepResolution.QUARTER_STEP:
            self._ms1_pin.state = 0
            self._ms2_pin.state = 1
        elif self._microstep_resolution == MicroStepResolution.EIGHTH_STEP:
            self._ms1_pin.state = 1
            self._ms2_pin.state = 1

    def close(self):
        super().close()

        self.pin_factory.release_all(self)
        
        all_pins = [
            self._step_pin,
            self._dir_pin,
            self._ms1_pin,
            self._ms2_pin,
            self._enable_pin,
        ]

        for pin in filter(None, all_pins):
            pin.close()

    def _stepOnce(self):
        raise NotImplementedError

    def step(self):
        raise NotImplementedError


