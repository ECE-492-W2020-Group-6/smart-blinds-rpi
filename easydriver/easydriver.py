from gpiozero import Device, GPIOPinMissing
from enum import IntEnum
import time

class MicroStepResolution(IntEnum):
    FULL_STEP = 0
    HALF_STEP = 1
    QUARTER_STEP = 2
    EIGHTH_STEP = 3

class StepDirection(IntEnum):
    FORWARD = 0
    REVERSE = 1

class PowerState(IntEnum):
    OFF = 0
    ON = 1

class EasyDriver(Device):
    def __init__(self,
            step_pin=None, 
            dir_pin=None, 
            ms1_pin=None, 
            ms2_pin=None, 
            enable_pin=None, 
            microstep_resolution=MicroStepResolution.FULL_STEP, **kwargs):
        super().__init__(**kwargs)

        # Init pins to None, useful in self.close()
        self._step_pin = None
        self._dir_pin = None
        self._ms1_pin = None
        self._ms2_pin = None
        self._enable_pin = None

        # Check if any pins are missing
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

        # Reserve pins and get ref of pin from factory
        # Set GPIO mode to output and set initial output state
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

        self.microstep_resolution = microstep_resolution
        self.power_state = PowerState.OFF
        self.direction = StepDirection.FORWARD

    @property
    def step_pin(self):
        return self._step_pin

    @property 
    def dir_pin(self):
        return self._dir_pin

    @property
    def enable_pin(self):
        return self._enable_pin

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
        
        time.sleep(200/1000000000) # Minimum Command Action Time (200 ns) - See Datasheet
    
    @property
    def power_state(self):
        return self._power_state

    @power_state.setter
    def power_state(self, state):
        self._power_state = state
        if state == PowerState.OFF:
            self._enable_pin.state = 1
        elif state == PowerState.ON:
            self._enable_pin.state = 0
            time.sleep(1/1000) # Maximum Wakeup Time (1.0 ms) - see Datasheet

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, direction):
        self._direction = direction 
        if direction == StepDirection.FORWARD:
            self._dir_pin.state = 0
        elif direction == StepDirection.REVERSE:
            self._dir_pin.state = 1
        time.sleep(200/1000000000) # Minimum Command Action Time (200 ns) - See Datasheet

    def _step_once(self):
        self._step_pin.state = 1 # Trigger one step
        time.sleep(1/1000000) #  Minimum Step Pulse Width (1.0 us) - See Datasheet
        self._step_pin.state = 0 # Pull step pin low so it can be triggered again
        time.sleep(1/1000000) # Minimum Step Low Time (1.0 us) - See Datasheet

        # Use delay to get smooth action
        # TODO: Adjust speed?
        time.sleep(0.1)

    def step(self, steps, direction=StepDirection.FORWARD):
        self.power_state = PowerState.ON
        self.direction = direction
        for _ in range(steps):
            self._step_once()
        self.power_state = PowerState.OFF

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
