'''
Unit tests for the API request handlers(server side)
TODO: Currrently just method stubs

Author: Alex (Yin) Chen
Creation Date: February 2, 2020
'''
import pytest
import datetime
from blinds.blinds_api import Blinds, SmartBlindsSystem
from blinds.blinds_schedule import BlindMode, ScheduleTimeBlock
from blinds.blinds_command import BlindsCommand
from requests import codes as RESP_CODES

'''
Class for testing the blinds API
TODO: Current is WIP, more work needed to first fill out the API code and extend it. 
'''
class TestSmartBlindsSystemApi:

    '''
    Test the handler for GET requests for temperature
    '''
    def test_getTemperature( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.getTemperature()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for GET requests for position
    '''
    def test_getPosition( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.getPosition()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for GET requests for status
    '''
    def test_getStatus( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.getStatus()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for GET requests for schedule
    '''
    def test_getSchedule( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.getSchedule()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for POST requests for schedule
    '''
    def test_postSchedule( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.postSchedule( "SCHEDULE" )[1] == RESP_CODES[ "ACCEPTED" ] )

    '''
    Test the handler for DELETE requests for schedule
    '''
    def test_deleteSchedule( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.deleteSchedule()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for POST requests for command
    '''
    def test_postBlindsCommand( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )

        command1 = BlindsCommand( BlindMode.MANUAL, 32, -5 )

        # not checking the response data for regular cases because it is taken from return values of 
        # BlindsCommand.toTimeBlock, which are tested in test_blindscommand
        assert ( blindsSystem.postBlindsCommand( BlindsCommand.toDict( command1 ) )[1] == RESP_CODES[ "ACCEPTED" ] )
