from gpiozero import Device, GPIOPinMissing
from enum import IntEnum
import time

"""Encapsulates microstep resolution of EasyDriver board
"""
class MicroStepResolution(IntEnum):
    FULL_STEP = 0
    HALF_STEP = 1
    QUARTER_STEP = 2
    EIGHTH_STEP = 3

"""Encapsulates direction of EasyDriver board
"""
class StepDirection(IntEnum):
    FORWARD = 0
    REVERSE = 1

"""Encapsulates state of power for EasyDriver Board
"""
class PowerState(IntEnum):
    OFF = 0
    ON = 1

"""Class provides software control of SparkFun EasyDriver Motor Controller Board
"""
class EasyDriver(Device):
    """[summary]
    
    Arguments:
        step_pin{int, string} -- Pin to control STEP GPIO signal on board
        dir_pin{int, string} -- Pin to control DIR GPIO signal on board
        ms1_pin{int, string} -- Pin to control MS1 GPIO signal on board
        ms2_pin{int, string} -- Pin to control MS2 GPIO signal on board
        enable_pin{int, string} -- Pin to control ENABLE GPIO signal on board
    
    Raises:
        GPIOPinMissing: No Step Pin Given
        GPIOPinMissing: No Dir Pin Given
        GPIOPinMissing: No MS1 Pin Given
        GPIOPinMissing: No MS2 Pin Given
        GPIOPinMissing: No Enable Pin Given
    """
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

    """Get's step pin
    
    Returns:
        gpiozero.PIN - Instance of STEP Pin
    """
    @property
    def step_pin(self):
        return self._step_pin

    """Get's dir pin

    Returns:
        gpiozero.PIN - Instance of DIR Pin
    """
    @property 
    def dir_pin(self):
        return self._dir_pin

    """Get's enable pin

    Returns:
        gpiozero.PIN - Instance of ENABLE Pin
    """
    @property
    def enable_pin(self):
        return self._enable_pin

    """Get's ms1 pin

    Returns:
        gpiozero.PIN - Instance of MS 1 Pin
    """
    @property
    def ms1_pin(self):
        return self._ms1_pin

    """Get's ms2 pin

    Returns:
        gpiozero.PIN - Instance of MS 2 Pin
    """
    @property
    def ms2_pin(self):
        return self._ms2_pin

    """Get's microstep revolution setting for driver

    Returns:
        MicroStepResolution - microstep resolution setting of driver
    """
    @property
    def microstep_resolution(self):
        return self._microstep_resolution 

    """[summary]

    Arguments:
        microstep_resolution {MicroStepResolution} - new microstep resolution setting
    """
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
    
    """Return power state
    
    Returns:
        PowerState -- current power state of driver
    """
    @property
    def power_state(self):
        return self._power_state

    """Set's new power state of driver

    Arguments:
        state {PowerState} - new power state of driver
    """
    @power_state.setter
    def power_state(self, state):
        self._power_state = state
        if state == PowerState.OFF:
            self._enable_pin.state = 1
        elif state == PowerState.ON:
            self._enable_pin.state = 0
            time.sleep(1/1000) # Maximum Wakeup Time (1.0 ms) - see Datasheet

    """Get's direction of driver
    
    Returns:
        StepDirection -- step direction of driver
    """
    @property
    def direction(self):
        return self._direction

    """Set's direction of driver

    Arguments:
        direction {StepDirection} --  new direction of driver
    """
    @direction.setter
    def direction(self, direction):
        self._direction = direction 
        if direction == StepDirection.FORWARD:
            self._dir_pin.state = 0
        elif direction == StepDirection.REVERSE:
            self._dir_pin.state = 1
        time.sleep(200/1000000000) # Minimum Command Action Time (200 ns) - See Datasheet

    """Makes one step in the current direction of the driver

    Note: this is a private method that is not meant to be called outside of the class.
    """
    def _step_once(self):
        self._step_pin.state = 1 # Trigger one step
        time.sleep(1/1000000) #  Minimum Step Pulse Width (1.0 us) - See Datasheet
        self._step_pin.state = 0 # Pull step pin low so it can be triggered again
        time.sleep(1/1000000) # Minimum Step Low Time (1.0 us) - See Datasheet

        # Use delay to get smooth action
        # TODO: Adjust speed?
        time.sleep(0.1)

    """Makes the specified number of steps in the specified direction

    Arguments:
        steps {int} -- number of steps
        direction {StepDirection} -- direction to step in
    """
    def step(self, steps, direction=StepDirection.FORWARD):
        self.power_state = PowerState.ON
        self.direction = direction
        for _ in range(steps):
            self._step_once()
        self.power_state = PowerState.OFF

    """Cleanup driver's resources
    """
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
