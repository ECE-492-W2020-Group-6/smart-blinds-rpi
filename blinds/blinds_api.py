'''
File for blinds API related code. 
Contains classes: 
    Blinds: an abstraction to model the blinds, gives functions for rotation and calls the motor driver
    SmartBlindsSystem: class to model the whole system, provides functions to handle API requests. 

Also contains custom exception classes to provide more specific exceptions for the smart blinds systems. 
Currently, these are: 
    InvalidBlindPositionException

Note, the API handlers are not implemented, and the dummy data there is used to indicate the intended format of 
the response data. 

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''
   
import bme280
from enum import Enum
import json
from requests import codes as RESP_CODES
import smbus2
from easydriver.easydriver import MicroStepResolution, StepDirection
import time
import datetime

from blinds.blinds_command import BlindsCommand
from blinds.blinds_schedule import BlindMode, BlindsSchedule, ScheduleTimeBlock, InvalidBlindsScheduleException, BlindSchedulingException
from controlalgorithm.angle_step_mapper import ANGLE_POSITION_FACTOR
from controlalgorithm.angle_step_mapper import NUM_STEPS_FACTOR
from controlalgorithm.angle_step_mapper import AngleStepMapper
from controlalgorithm.persistent_data import get_motor_position
from controlalgorithm.persistent_data import set_motor_position
from controlalgorithm.max_sunlight_algorithm import max_sunlight_algorithm
from controlalgorithm.composite_algorithm import composite_algorithm
from controlalgorithm.heat_mgmt_algorithm import heat_mgmt_algorithm
from easydriver.easydriver import EasyDriver, PowerState, MicroStepResolution, StepDirection
from piserver.api_routes import *
import threading

'''
Class to model blinds as an abstraction. 
Gives the ability to control blinds position 
'''
class Blinds:
    # Public attributes
    step_resolution = MicroStepResolution.FULL_STEP

    # Private attributes
    _motorDriver = None
    _angleStepMapper = None
    # current position of the blinds as a rotational % 0 is horizontal, 100 is fully closed "up" position, -100 is fully closed "down" position
    _currentPosition = None 

    '''
    Constuctor. Set the motor driver.
    Set driver to None to allow for testing without a driver. 
    '''
    def __init__( self, driver, mapper ):
        self._motorDriver = driver
        self._angleStepMapper = mapper
        self._currentPosition = get_motor_position() * ( 1/ANGLE_POSITION_FACTOR )

    '''
    Gets current position of blinds.
    '''
    @property 
    def currentPosition( self ):
        return self._currentPosition

    '''
    Resets the blinds to the 0% tilt position (horizontal slats)
    '''
    def reset_position( self ):
        print( "resetting to horizontal position" )

        motor_position = get_motor_position() # in degrees from [-90,90]

        if motor_position != 0:
            num_steps, motor_dir = self._angleStepMapper.map_angle_to_step(0, self.step_resolution)
            self._motorDriver.microstep_resolution = self.step_resolution
            self._motorDriver.step(steps=num_steps, direction=motor_dir)
            set_motor_position(0)

        self._currentPosition = 0

        pass

    '''
    Adjust blinds to the position specified as a percentage in [-100%, 100%]
    '''
    def rotateToPosition( self, position ):
        if ( position > 100 or position < -100 ):
            raise InvalidBlindPositionException( "Position must be between -100 and 100")

        print( "rotating to {}%".format( position ) )

        desired_tilt_angle = position * ANGLE_POSITION_FACTOR
        
        num_steps, motor_dir = self._angleStepMapper.map_angle_to_step(desired_tilt_angle, self.step_resolution)

        num_steps = round(num_steps * NUM_STEPS_FACTOR)

        self._motorDriver.microstep_resolution = self.step_resolution
        self._motorDriver.step(steps=num_steps, direction=motor_dir)

        #DEBUG
        print("resolution: ", self.step_resolution, "num_steps: ", num_steps, "direction: ", motor_dir)

        set_motor_position(desired_tilt_angle)

        self._currentPosition = position

    '''
    Re-define 0 position after user manually places blinds
    '''
    def calibratePosition( self ):
        set_motor_position( 0 )
        self._currentPosition = 0


'''
Class for modelling the smart blinds system as a whole
Provides functions for API requests
'''
class SmartBlindsSystem:
    _blinds = None
    _blindsSchedule = None
    _temperatureSensor = None

    '''
    Costructor for modelling the system of blinds as a whole. 
    Provides functions for API requests

    Arguments:
        blinds : a Blinds object for controlling the blinds themselves. This is currently left as a single object for proof 
            concept, but can be extended to a list of Blinds objects for controlling multiple blinds throughout the house
        blindsSchedule : a BlindsSchedule object to control the schedule of the blinds
        temperatureSensor : an abstraction of the temperature sensor controls 
    '''
    def __init__( self, blinds, blindsSchedule, temperatureSensor ):
        self._blinds = blinds 
        self._blindsSchedule = blindsSchedule
        self._temperatureSensor = temperatureSensor

        # the currently active manual command, if any 
        # self._activeCommandTimeBlock should be set to a ScheduleTimeBlock 
        self._activeCommandTimeBlock = None

    # ---------- API functions --------- #
    '''
    API GET request handler for temperature
    URL: TEMPERATURE_ROUTE
    TODO: METHOD STUB 
    '''
    def getTemperature( self ):
        print( "processing request for GET temperature")
        
        try:
            data = {
                "temperature" : str(self._temperatureSensor.getSample()),
                "temp_units" : "C"
            }

            return ( data, RESP_CODES[ "OK" ] )
        except Exception as err:
            return ( str(err), RESP_CODES[ "BAD_REQUEST" ] )

    '''
    API GET request handler for position
    URL: POSITION_ROUTE
    '''
    def getPosition( self ):
        print( "processing request for GET position")
        
        try:
            data = {
                "position" : str(self._blinds.currentPosition),
            }
            return ( data, RESP_CODES[ "OK" ] )
        except Exception as err:
            return ( str(err), RESP_CODES[ "BAD_REQUEST" ] )

    '''
    API POST request handler for position
    URL: POSITION_ROUTE
    '''
    def postPosition( self, data ):
        print( f"processing request for POST position, data: {data}" )
        try:
            position = data["position"]
            self._blinds.rotateToPosition(position)
            return ( {}, RESP_CODES[ "OK" ] )
        except Exception as err:
            return ( str(err), RESP_CODES[ "BAD_REQUEST" ] )

    '''
    API POST request handler for position calibration
    URL: CALIBRATE_POSITION_ROUTE
    '''
    def postCalibratePosition( self ):
        try:
            self._blinds.calibratePosition()
            return ( {}, RESP_CODES[ "OK" ] )
        except Exception as err:
            return ( str(err), RESP_CODES[ "BAD_REQUEST" ] )

    '''
    API GET request handler for status
    URL: STATUS_ROUTE
    '''
    def getStatus( self ):
        try:
            data = {
                "position" : str(self._blinds.currentPosition),
                "temperature" : str(self._temperatureSensor.getSample()),
                "temp_units" : "C"
            }
            return ( data, RESP_CODES[ "OK" ] )
        except Exception as err:
            return ( str(err), RESP_CODES[ "BAD_REQUEST" ] )
    
    '''
    API GET request handler for schedule
    URL: SCHEDULE_ROUTE
    TODO: METHOD STUB 
    '''
    def getSchedule( self ):
        print( "processing request for GET schedule")
        
        try:
            # data =  BlindsSchedule.toJson( self._blindsSchedule )
            data = BlindsSchedule.toDict( self._blindsSchedule )

            resp = ( data, RESP_CODES[ "OK" ] )

        # TODO Other error cases

        except Exception as err: # catch all others and return an error message 
            # TODO : More specialized handling for safety, we don't want just any error messages being spit to the user, for 
            # now, in the testing phase we return the error 
            return str( err ), RESP_CODES[ "BAD_REQUEST" ]

        return resp

    '''
    API POST request handler for motor test
    URL: MOTOR_TEST_ROUTE
    '''
    def testMotor( self ):
        print( "processing request for POST motor test")
        
        try:
            self._blinds._motorDriver.microstep_resolution = MicroStepResolution.FULL_STEP
            self._blinds._motorDriver.step(steps=200, direction=StepDirection.FORWARD)

            return ( {}, RESP_CODES[ "OK" ] )
        except Exception as err:
            return ( str(err), RESP_CODES[ "BAD_REQUEST" ] )

    '''
    API POST request handler for schedule. For now accept only POST request of a full schedule

    Set forceUpdate to true for immediate update.

    URL: SCHEDULE_ROUTE
    '''
    def postSchedule( self, schedule, forceUpdate=False ):
        print( "processing request for POST schedule")
        print( "received schedule=\n", schedule )

        try:
            self._blindsSchedule = BlindsSchedule.fromDict( schedule )

            if forceUpdate:
                self.check_state_and_update()

            return schedule, RESP_CODES[ "ACCEPTED" ]

        except ( InvalidBlindsScheduleException, BlindSchedulingException ) as err:
            return str( err ), RESP_CODES[ "BAD_REQUEST" ]

        except Exception as err: # catch all others and return an error message 
            #TODO : More specialized handling for safety, we don't want just any error messages being spit to the user, for 
            # now, in the testing phase we return the error 
            return str( err ), RESP_CODES[ "BAD_REQUEST" ]

    '''
    API DELETE request handler for schedule. Deletes the currently active schedule. 

    Set forceUpdate to true for immediate update.

    URL: SCHEDULE_ROUTE
    '''
    def deleteSchedule( self, forceUpdate=False ):
        print( "processing request for DELETE schedule")

        try:
            # reset the schedule to an empty schedule, but keep the current default behavior 
            self._blindsSchedule._schedule = {
                BlindsSchedule.SUNDAY : [],
                BlindsSchedule.MONDAY : [],
                BlindsSchedule.TUESDAY : [],
                BlindsSchedule.WEDNESDAY : [],
                BlindsSchedule.THURSDAY : [],
                BlindsSchedule.FRIDAY : [],
                BlindsSchedule.SATURDAY : []
            }

            if forceUpdate:
                # force update on current state
                self.check_state_and_update()

            return BlindsSchedule.toDict( self._blindsSchedule ), RESP_CODES[ "OK" ]

        except Exception as err: # catch all others and return an error message 
            #TODO : More specialized handling for safety, we don't want just any error messages being spit to the user, for 
            # now, in the testing phase we return the error 
            return str( err ), RESP_CODES[ "BAD_REQUEST" ]
 
    '''
    API POST request handler for command
    Handles a command (dict) of the form 
    {
        "mode" : a string name from the BlindMode enum
        "position" : integer between -100 and 100
        "duration" : positive integer minutes
    }
    if time is given value 0, this is change will remain until the next day

    Set forceUpdate to true for immediate update.

    URL: COMMAND_ROUTE
    '''
    def postBlindsCommand( self, command, forceUpdate=False ):
        print( "processing request for POST command")
        try:
            blindsCommand = BlindsCommand.fromDict( command )

            # update active command, use custome time provider to insert a timezone
            self._activeCommandTimeBlock = blindsCommand.toTimeBlock( 
                    currentTimeProvider=datetime.datetime.now( self._blindsSchedule._timezone ).time )

            # return the resulting time block from the command
            data = ScheduleTimeBlock.toDict( self._activeCommandTimeBlock ) or {}

            if forceUpdate:
                # Update current state based on the command
                self.check_state_and_update()

            return data, RESP_CODES[ "ACCEPTED" ]   

        except Exception as err:
            return ( str(err), RESP_CODES[ "BAD_REQUEST" ] )

    '''
    API DELETE request handler for command 
    This should be used to clear the currently active command, restoring the blinds to the scheduled behaviour.

    Set forceUpdate to true for immediate update.

    URL: COMMAND_ROUTE
    '''
    def deleteBlindsCommand( self, forceUpdate=False ): 
        print( "processing request for DELETE command")
        self._activeCommandTimeBlock = None

        # Force system update to move blinds to desired position
        if forceUpdate:
            self.check_state_and_update()

        return {}, RESP_CODES[ "OK" ]
    
    # ---------- END OF API functions --------- #

    '''
    Start the main loop for the system. This performs checks of the system state, ie. what is currently scheduled or
    current commands and defaults. This will generate a new thread (thus sharing the memory space) to allow the same 
    SmartBlindsSystem object.  
    
    This performs checks of the "environment", such as the temperature and weather data
    '''
    def activate_main_loop( self, iter_per_min=1 ): 
        sleep_time = 60 / iter_per_min

        '''
        Inner function of the actual main loop to execute.        
        '''
        def main_loop():   
            while True: 
                print( "Performing main loop iteration" )
                # TODO: what happens in an iteration
                self.check_state_and_update()
                time.sleep( sleep_time )

        thread = threading.Thread(target=main_loop)
        thread.start()

    '''
    Single iteration of the main loop.
    
    '''
    def check_state_and_update( self ):
        current_datetime = datetime.datetime.now( self._blindsSchedule._timezone )
        current_time = current_datetime.time()
        print( "Checking and updating at time: ", current_time )

        # check active command. apply or clear the command
        if self._activeCommandTimeBlock is not None:
            check_time_result = self._activeCommandTimeBlock.checkTime( current_time )

            # case 1: current time is before the command duration
            # ignore and do nothing, this means the command does not have to be dealt with yet

            # case 2: current time is within the command duration
            if check_time_result == 0:
                print( "DEBUG: Found an applicable command.", ScheduleTimeBlock.toJson( self._activeCommandTimeBlock ) )
                self.do_blinds_update( self._activeCommandTimeBlock._mode, self._activeCommandTimeBlock._position )
                return

            # case 3: current time is after the command duration
            elif check_time_result == 1:
                # clear the current command, it is no longer valid
                self._activeCommandTimeBlock = None
                
        # At this point, there is no need to deal with manual commands. Check the schedule for a time block
        current_weekday_index = current_datetime.weekday()
        current_weekday_name = BlindsSchedule.DAYS_OF_WEEK[ current_weekday_index ]

        day_sched = self._blindsSchedule._schedule.get( current_weekday_name )

        active_schedule_block = None
        for block in day_sched:
            if block.checkTime( current_time ) == 0:
                active_schedule_block = block
                break

        # found a time block correspoding to current time
        if active_schedule_block is not None: 
            print( "DEBUG: Found an applicable scheduled block.", ScheduleTimeBlock.toJson( active_schedule_block ) )
            self.do_blinds_update( active_schedule_block._mode, active_schedule_block._position )
            return 

        # At this point, no time block was found, so we go to the default behaviour
        print( "DEBUG: Using defaults. Mode=", self._blindsSchedule._default_mode.name, " Pos=", self._blindsSchedule._default_pos )
        self.do_blinds_update( self._blindsSchedule._default_mode, self._blindsSchedule._default_pos )
        return 


    '''
    Perform update to motor and controls as needed.
    '''
    def do_blinds_update( self, target_mode, target_pos=None ):
        position = target_pos

        if target_mode == BlindMode.MANUAL:
            # pass for this case, target position is already known
            pass

        # for other modes, calculate the correct target position
        elif target_mode == BlindMode.LIGHT:
            # convert angle to position
            position = int( max_sunlight_algorithm() / ANGLE_POSITION_FACTOR )

        elif target_mode == BlindMode.DARK:
            # treat -100% as the DARK mode
            position = -100

        elif target_mode == BlindMode.ECO:
            # convert angle to position
            position = int( heat_mgmt_algorithm( self._temperatureSensor ) / ANGLE_POSITION_FACTOR )

        elif target_mode == BlindMode.BALANCED:
            # convert angle to position
            position = int( composite_algorithm( self._temperatureSensor ) / ANGLE_POSITION_FACTOR )

        # prevent unnecessary rotations
        if position != self._blinds._currentPosition:
            self._blinds.rotateToPosition( position )
        else:
            print( "DEBUG: No rotation, position has not changed" )

# ---------- Custom Exception classes --------- #
# Thrown when an position outside of [-100, 100] is given to rotateToPositions
class InvalidBlindPositionException( Exception ):
    pass

# ---------- END OF Custom Exception classes --------- #
