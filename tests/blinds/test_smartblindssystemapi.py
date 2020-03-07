'''
Unit tests for the API request handlers(server side)
TODO: Currrently just method stubs

Author: Alex (Yin) Chen
Creation Date: February 2, 2020
'''
import pytest
from blinds.blinds_api import Blinds, SmartBlindsSystem
from tempsensor.tempsensor import MockTemperatureSensor
from requests import codes as RESP_CODES

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
        yield SmartBlindsSystem( Blinds( None ), None, MockTemperatureSensor() )

    '''
    Test the handler for GET requests for temperature
    '''
    def test_getTemperature( self, blindsSystem ):
        assert ( blindsSystem.getTemperature()[1] == RESP_CODES[ "OK" ] )

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
    Test the handler for POST requests for schedule
    '''
    def test_postSchedule( self, blindsSystem ):
        assert ( blindsSystem.postSchedule( "SCHEDULE" )[1] == RESP_CODES[ "ACCEPTED" ] )

    '''
    Test the handler for DELETE requests for schedule
    '''
    def test_deleteSchedule( self, blindsSystem ):
        assert ( blindsSystem.deleteSchedule()[1] == RESP_CODES[ "OK" ] )

    '''
    Test the handler for POST requests for command
    '''
    def test_postBlindsCommand( self, blindsSystem ):
        assert ( blindsSystem.postBlindsCommand( 5, 1 )[1] == RESP_CODES[ "ACCEPTED" ] )
