'''
Unit tests for the API request handlers(server side)
TODO: Currrently just method stubs

Author: Alex (Yin) Chen
Creation Date: February 2, 2020
'''
import pytest
import datetime
from blinds.blinds_api import Blinds, SmartBlindsSystem
from blinds.blinds_schedule import BlindMode, ScheduleTimeBlock, BlindsSchedule
from blinds.blinds_command import BlindsCommand
from tempsensor.tempsensor import MockTemperatureSensor
from requests import codes as RESP_CODES
from unittest.mock import MagicMock

'''
Class for testing the blinds API
TODO: Current is WIP, more work needed to first fill out the API code and extend it. 
'''
class TestSmartBlindsSystemApi:

    '''Creates and returns a fresh instance of the blinds system for each test case
    
    Yields:
        SmartBlindsSystem -- fresh instance of smart blinds system for each test
    '''
    @pytest.fixture()
    def blindsSystem( self ):
        yield SmartBlindsSystem( Blinds( None ), BlindsSchedule( BlindMode.DARK ), MockTemperatureSensor(), None )

    '''
    Test the handler for GET requests for temperature
    '''
    def test_getTemperature( self, blindsSystem ):
        assert ( blindsSystem.getTemperature()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for GET requests for temperature when exception occurs
    '''
    def test_getTemperature_with_exception(self):
        tempSensor = MockTemperatureSensor()
        tempSensor.getSample = MagicMock(side_effect=Exception)
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, tempSensor )
        assert ( blindsSystem.getTemperature()[1] == RESP_CODES[ "BAD_REQUEST" ] )

    '''
    Test the handler for GET requests for position
    '''
    def test_getPosition( self, blindsSystem ):
        assert ( blindsSystem.getPosition()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for GET requests for status
    '''
    def test_getStatus( self, blindsSystem ):
        assert ( blindsSystem.getStatus()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for GET requests for schedule
    '''
    def test_getSchedule( self, blindsSystem ):
        assert ( blindsSystem.getSchedule()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for POST requests for schedule. Uses an arbitrary schedule
    '''
    def test_postSchedule( self, blindsSystem ):
        test_sched = BlindsSchedule( BlindMode.DARK, schedule={
            BlindsSchedule.SUNDAY: [
                ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.LIGHT, None ), 
                ScheduleTimeBlock( datetime.time( 5, 00), datetime.time( 7, 00 ), BlindMode.MANUAL, 15 )
            ],
            BlindsSchedule.MONDAY : [ 
                ScheduleTimeBlock( datetime.time( 12, 00), datetime.time( 15, 00 ), BlindMode.LIGHT, None ),
                ScheduleTimeBlock( datetime.time( 4, 3), datetime.time( 6, 00 ), BlindMode.LIGHT, None )
            ],
            BlindsSchedule.TUESDAY: [
                ScheduleTimeBlock( datetime.time( 10, 22), datetime.time( 12, 00 ), BlindMode.DARK, None )
            ],
            BlindsSchedule.WEDNESDAY: [],
            BlindsSchedule.THURSDAY: [],
            BlindsSchedule.FRIDAY: [
                ScheduleTimeBlock( datetime.time( 22, 44), datetime.time(23, 00 ), BlindMode.LIGHT, None ), 
                ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.ECO, None ), 
                ScheduleTimeBlock( datetime.time( 00, 32), datetime.time( 1, 00 ), BlindMode.LIGHT, None )
            ],
            BlindsSchedule.SATURDAY: []
        } )


        assert ( blindsSystem.postSchedule( BlindsSchedule.toDict( test_sched ) )[1] == RESP_CODES[ "ACCEPTED" ] )

    '''
    Test the handler for DELETE requests for schedule
    '''
    def test_deleteSchedule( self, blindsSystem ):
        assert ( blindsSystem.deleteSchedule()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for POST requests for command
    '''
    def test_postBlindsCommand( self, blindsSystem ):
        command1 = BlindsCommand( BlindMode.MANUAL, 32, -5 )

        # not checking the response data for regular cases because it is taken from return values of 
        # BlindsCommand.toTimeBlock, which are tested in test_blindscommand
        assert ( blindsSystem.postBlindsCommand( BlindsCommand.toDict( command1 ) )[1] == RESP_CODES[ "ACCEPTED" ] )
