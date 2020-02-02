import pytest
from blinds.blinds_api import Blinds, SmartBlindsSystem
from requests import codes as RESP_CODES

'''
Unit tests for the API request handlers(server side)
TODO: Currrently just method stubs
'''
class TestSmartBlindsSystemApi:

    def test_getTemperature( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.getTemperature()[1] == RESP_CODES[ "OK" ] )

    def test_getPosition( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.getPosition()[1] == RESP_CODES[ "OK" ] )

    def test_getStatus( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.getStatus()[1] == RESP_CODES[ "OK" ] )

    def test_getSchedule( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.getSchedule()[1] == RESP_CODES[ "OK" ] )

    def test_postSchedule( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.postSchedule( "SCHEDULE" )[1] == RESP_CODES[ "ACCEPTED" ] )

    def test_deleteSchedule( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.deleteSchedule()[1] == RESP_CODES[ "OK" ] )

    def test_postBlindsCommand( self ):
        blindsSystem = SmartBlindsSystem( Blinds( None ), None, None )
        assert ( blindsSystem.postBlindsCommand( 5, 1 )[1] == RESP_CODES[ "ACCEPTED" ] )