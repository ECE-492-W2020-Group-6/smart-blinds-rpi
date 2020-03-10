'''
File for blinds API related code. 
Contains classes: 
    Blinds: an abstraction to model the blinds, gives functions for rotation and callse the motor driver
    SmartBlindsSystem: class to model the whole system, provides functions to handle API requests. 

Also contains custom exception classes to provide more specific exceptions for the smart blinds systems. 
Currently, these are: 
    InvalidBlindPositionException

Note, the API handlers are not implemented, and the dummy data there is used to indicate the intended format of 
the response data. 

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''
from requests import codes as RESP_CODES
from piserver.api_routes import *
from enum import Enum
from blinds.blinds_schedule import BlindsSchedule, ScheduleTimeBlock, InvalidBlindsScheduleException, BlindSchedulingException
import json
from blinds.blinds_command import BlindsCommand
import bme280
import smbus2

'''
Class to model blinds as an abstraction. 
Gives the ability to control blinds position 
'''
class Blinds:
    # Public attributes

    # Private attributes
    _motorDriver = None

    # current position of the blinds as a rotational %
    # 0 is horizontal, 100 is fully closed "up" positioin, -100 is fully closed "down" position
    _currentPosition = None 

    '''
    Constuctor. Set the motor driver.
    Set driver to None to allow for testing without a driver. 
    TODO fill in other setup procedures for hardware. 
    '''
    def __init__( self, driver, startingPos = 0 ):
        self._motorDriver = driver
        self._currentPosition = startingPos

        # TODO: OTHER SETUP PROCEDURES
        pass

    '''
    Resets the blinds to the 0% tilt position (horizontal slats)
    TODO: METHOD STUB
    '''
    def reset_position( self ):
        print( "resetting to horizontal position" )

        if self._motorDriver is not None: 
            # control motor using the driver
            pass

        self._currentPosition = 0

        pass

    '''
    Adjust blinds to the position specified as a percentage in [-100%, 100%]
    TODO: METHOD STUB 
    '''
    def rotateToPosition( self, position ):
        if ( position > 100 or position < -100 ):
            raise InvalidBlindPositionException( "Position must be between -100 and 100")

        print( "rotating to {}%".format( position ) )

        if self._motorDriver is not None: 
            # control motor using the driver
            pass

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

    '''
    Costructor for modelling the system of blinds as a whole. 
    Provides functions for API requests

    Arguments:
        blinds : a Blinds object for controlling the blinds themselves. This is currently left as a single object for proof 
            concept, but can be extended to a list of Blinds objects for controlling multiple blinds throughout the house
        blindsSchedule : a BlidnsSchedule object to control the schedule of the blinds
        temperatureHandler : an abstraction of the temperature sensor controls 
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
    API POST request handler for schedule. For now accept only POST request of a full schedule
    URL: SCHEDULE_ROUTE
    TODO: METHOD STUB 
    '''
    def postSchedule( self, schedule ):
        print( "processing request for POST schedule")
        print( "received schedule=\n", schedule )

        try:
            self._blindsSchedule = BlindsSchedule.fromDict( schedule )
            return schedule, RESP_CODES[ "ACCEPTED" ]

        except ( InvalidBlindsScheduleException, BlindSchedulingException ) as err:
            return str( err ), RESP_CODES[ "BAD_REQUEST" ]

        except Exception as err: # catch all others and return an error message 
            #TODO : More specialized handling for safety, we don't want just any error messages being spit to the user, for 
            # now, in the testing phase we return the error 
            return str( err ), RESP_CODES[ "BAD_REQUEST" ]

    '''
    API DELETE request handler for schedule
    URL: SCHEDULE_ROUTE
    TODO: METHOD STUB 
    '''
    def deleteSchedule( self ):
        print( "processing request for DELETE schedule")

        try:
            # reset the schedule to an empty schedule, but keep the current default behavior 
            curr_default_mode = self._blindsSchedule._default_mode
            curr_default_pos = self._blindsSchedule._default_pos
            self._blindsSchedule = BlindsSchedule( curr_default_mode, curr_default_pos )

            return BlindsSchedule.toDict( self._blindsSchedule ), RESP_CODES[ "OK" ]

        # TODO Other error cases

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
