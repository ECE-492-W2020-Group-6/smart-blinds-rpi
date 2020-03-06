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
from blinds.blinds_schedule import BlindsSchedule
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
        self._currentPosition = position
        pass


'''
Class for modelling the smart blinds system as a whole
Provides functions for API requests
'''
class SmartBlindsSystem:
    _blinds = None
    _blindsSchedule = None
    _temperatureHandler = None

    def __init__( self, blinds, blindsSchedule, temperatureHandler ):
        self._blinds = blinds 
        self._blindsSchedule = blindsSchedule
        self._temperatureHandler = temperatureHandler

    # ---------- API functions --------- #
    '''
    API GET request handler for temperature
    URL: TEMPERATURE_ROUTE
    TODO: METHOD STUB 
    '''
    def getTemperature( self ):
        print( "processing request for GET temperature")

        #Calibration parameters for the temperature sensor (Bosch BME280)
        #i2cdetect -y 1
        #https://pypi.org/project/RPi.bme280/
        #https://www.waveshare.com/wiki/BME280_Environmental_Sensor
        #https://www.waveshare.com/w/upload/7/75/BME280_Environmental_Sensor_User_Manual_EN.pdf
        port = 1
        address = 0x77
        bus = smbus2.SMBus(port)
        calibration_params = bme280.load_calibration_params(bus, address)

        # take a single reading and return a compensated_reading object
        sample = bme280.sample(bus, address, calibration_params)

        # get the temperature attribute from the compensated_reading class 
        int_temp = sample.temperature

        # dummy temporary data
        data = {
            "temperature" : str(int_temp),
            "temp_units" : "C"
        }

        resp = ( data, RESP_CODES[ "OK" ])

        # TODO: ERROR CASE 

        return resp

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
    Handles a command of the form 
    {
        "position" : integer between -100 and 100
        "time" : positive integer minutes
    }
    if time is given value 0, this is change will not be reverted
    URL: COMMAND_ROUTE
    TODO: METHOD STUB 
    '''
    def postBlindsCommand( self, position, time ):
        print( "processing request for POST command")

        # dummy data for return
        data = {
            "position" : position,
            "time" : time
        }
        # TODO: ERROR CASE 

        return data, RESP_CODES[ "ACCEPTED" ]   
    # ---------- END OF API functions --------- #

# ---------- Custom Exception classes --------- #
# Thrown when an position outside of [-100, 100] is given to rotateToPositions
class InvalidBlindPositionException( Exception ):
    pass

# ---------- END OF Custom Exception classes --------- #
