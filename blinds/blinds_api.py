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
from requests import codes as RESP_CODES
import smbus2

from piserver.api_routes import *
from blinds.blinds_schedule import BlindsSchedule, ScheduleTimeBlock
from blinds.blinds_command import BlindsCommand
import controlalgorithm.angle_step_mapper
from controlalgorithm.angle_step_mapper import AngleStepMapper
from controlalgorithm.persistent_data import get_motor_position
from controlalgorithm.persistent_data import set_motor_position
from easydriver.easydriver import EasyDriver, PowerState, MicroStepResolution, StepDirection

'''
Class to model blinds as an abstraction. 
Gives the ability to control blinds position 
'''
class Blinds:
    # Public attributes
    step_size = MicroStepResolution.FULL_STEP

    # Private attributes
    _motorDriver = None
    _angleStepMapper = None

    # current position of the blinds as a rotational %
    # 0 is horizontal, 100 is fully closed "up" positioin, -100 is fully closed "down" position
    _currentPosition = None 

    '''
    Constuctor. Set the motor driver.
    TODO fill in other setup procedures for hardware. 
    '''
    def __init__( self, driver, mapper, startingPos = 0 ):
        self._motorDriver = driver
        self._angleStepMapper = mapper
        self._currentPosition = startingPos

        # TODO: OTHER SETUP PROCEDURES
        pass

    '''
    Resets the blinds to the 0% tilt position (horizontal slats)
    TODO: Testing
    '''
    def reset_position( self ):
        print( "resetting to horizontal position" )

        motor_position = get_motor_position() # in degrees from [-90,90]
        angle_change = 0 - motor_position
        if motor_position != 0:
            num_steps, motor_dir = self._angleStepMapper.map_angle_to_step(angle_change, self.step_size)
            self._motorDriver.microstep_resolution = self.step_size
            self._motorDriver.step(steps=num_steps, direction=motor_dir)
            set_motor_position(0)

        self._currentPosition = 0
        pass

    '''
    Adjust blinds to the position specified as a percentage in [-100%, 100%]
    TODO: Testing
    '''
    def rotateToPosition( self, position ):
        if ( position > 100 or position < -100 ):
            raise InvalidBlindPositionException( "Position must be between -100 and 100")

        print( "rotating to {}%".format( position ) )

        desired_tilt_angle = position * angle_step_mapper.ANGLE_POSITION_FACTOR
        motor_position = get_motor_position() # in degrees from [-90,90]
        angle_change = desired_tilt_angle - motor_position
        num_steps, motor_dir = self._angleStepMapper.map_angle_to_step(angle_change, self.step_size)
        self._motorDriver.microstep_resolution = self.step_size
        self._motorDriver.step(steps=num_steps, direction=motor_dir)
        set_motor_position(desired_tilt_angle)

        self._currentPosition = position
        pass


'''
Class for modelling the smart blinds system as a whole
Provides functions for API requests
'''
class SmartBlindsSystem:
    _blinds = None
    _blindsSchedule = None
    _temperatureSensor = None

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
    TODO: METHOD STUB 
    '''
    def getPosition( self ):
        print( "processing request for GET position")
        
        # dummy temporary data
        data = {
            "position" : "15"
        }

        resp = ( data, RESP_CODES[ "OK" ] )

        # TODO: ERROR CASE 

        return resp

    '''
    API GET request handler for status
    URL: STATUS_ROUTE
    TODO: METHOD STUB 
    '''
    def getStatus( self ):
        print( "processing request for GET status")
        
        # dummy temporary data
        data = {
            "position" : "-30",
            "temperature" : "18",
            "temp_units" : "C"
        }

        resp = ( data, RESP_CODES[ "OK" ] )

        # TODO: ERROR CASE 

        return resp
    
    '''
    API GET request handler for schedule
    URL: SCHEDULE_ROUTE
    TODO: METHOD STUB 
    '''
    def getSchedule( self ):
        print( "processing request for GET schedule")
        
        # dummy temporary data
        # TODO: schedule will likely need to be serialized
        data = {
            "schedule" : "SCHEDULE"
        }

        resp = ( data, RESP_CODES[ "OK" ] )

        # TODO: ERROR CASE 

        return resp

    '''
    API POST request handler for schedule
    URL: SCHEDULE_ROUTE
    TODO: METHOD STUB 
    '''
    def postSchedule( self, schedule ):
        print( "processing request for POST schedule")
        print( "schedule=\n", schedule )

        # TODO: ERROR CASE 
        # TODO: CREATE CASE RESP_CODES[ "CREATED" ] (201)

        return schedule, RESP_CODES[ "ACCEPTED" ]

    '''
    API DELETE request handler for schedule
    URL: SCHEDULE_ROUTE
    TODO: METHOD STUB 
    '''
    def deleteSchedule( self ):
        print( "processing request for DELETE schedule")

        # TODO: ERROR CASE 

        return "{}", RESP_CODES[ "OK" ]

    '''
    API POST request handler for command
    Handles a command (dict) of the form 
    {
        "mode" : a string name from the BlindMode enum
        "position" : integer between -100 and 100
        "duration" : positive integer minutes
    }
    if time is given value 0, this is change will remain until the next day

    URL: COMMAND_ROUTE
    TODO: Testing 
    '''
    def postBlindsCommand( self, command ):
        print( "processing request for POST command")
        try:
            blindsCommand = BlindsCommand.fromDict( command )

            # update active command 
            self._activeCommandTimeBlock = blindsCommand.toTimeBlock()

            # return the resulting time block from the command
            data = ScheduleTimeBlock.toDict( self._activeCommandTimeBlock ) or {}
            return data, RESP_CODES[ "ACCEPTED" ]   

            # TODO: Update current state based on the command

        except Exception as err:
            return ( str(err), RESP_CODES[ "BAD_REQUEST" ] )

    '''
    API DELETE request handler for command 
    This should be used to clear the currently active command, restoring the blinds to the scheduled behaviour.

    URL: COMMAND_ROUTE
    '''
    def deleteBlindsCommand( self ): 
        print( "processing request for DELETE command")
        self._activeCommandTimeBlock = None

        # TODO: Force system update to move blinds to desired position

        # TODO: ERROR CASE 

        return {}, RESP_CODES[ "OK" ]
    
    # ---------- END OF API functions --------- #

# ---------- Custom Exception classes --------- #
# Thrown when an position outside of [-100, 100] is given to rotateToPositions
class InvalidBlindPositionException( Exception ):
    pass

# ---------- END OF Custom Exception classes --------- #
