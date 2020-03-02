'''
Unit tests for the ScheduleTimeBlock to verify the input validation and serialization

Author: Alex (Yin) Chen
Creation Date: February 20, 2020
'''

import pytest
import datetime
import json
from blinds.blinds_schedule import BlindMode, ScheduleTimeBlock, InvalidTimeBlockException

class TestScheduleTimeBlock: 

    '''
    Test for constructor and basic validate with no errors
    '''
    def test_constructor( self ):
        startTime = datetime.time( 3, 41 )
        endTime = datetime.time( 12, 41 )
        mode = BlindMode.MANUAL
        position = 7
        timeBlock = ScheduleTimeBlock( startTime, endTime, mode, position )

        assert( timeBlock._start == startTime )
        assert( timeBlock._end == endTime )
        assert( timeBlock._mode == mode )
        assert( timeBlock._position == position )

    '''
    Test for update and basic validate with no errors
    '''
    def test_update( self ):
        startTime = datetime.time( 3, 41 )
        endTime = datetime.time( 12, 41 )
        mode = BlindMode.MANUAL
        position = 7
        timeBlock = ScheduleTimeBlock( startTime, endTime, mode, position )

        newStart = datetime.time( 15, 41 )
        newEnd = datetime.time( 18, 9 )
        newMode = BlindMode.DARK

        timeBlock.update( newStart, newEnd, newMode )

        assert( timeBlock._start == newStart )
        assert( timeBlock._end == newEnd )
        assert( timeBlock._mode == newMode )
        assert( timeBlock._position == None )

    '''
    Test for validate with invalid times
    '''
    def test_invalidTime( self ):
        startTime = datetime.time( 11, 11 )
        endTime = datetime.time( 17, 55 )
        mode = BlindMode.MANUAL
        position = 7

        timeBlock = ScheduleTimeBlock( startTime, endTime, mode, position )
        timeBlock._start = endTime
        timeBlock._end = startTime

        with pytest.raises( InvalidTimeBlockException ):
            timeBlock.validate()

    '''
    Test for validate with invalid mode
    '''
    def test_invalidMode( self ):
        startTime = datetime.time( 11, 11 )
        endTime = datetime.time( 17, 55 )
        mode = BlindMode.MANUAL
        position = 7

        timeBlock = ScheduleTimeBlock( startTime, endTime, mode, position )
        timeBlock._mode = 9 # not a valid mode

        with pytest.raises( InvalidTimeBlockException ):
            timeBlock.validate()

    '''
    Test for validate with invalid position
    '''
    def test_invalidPosition( self ):
        startTime = datetime.time( 11, 11 )
        endTime = datetime.time( 17, 55 )
        mode = BlindMode.MANUAL
        position = 7

        timeBlock = ScheduleTimeBlock( startTime, endTime, mode, position )
        timeBlock._position = -101 # not a valid position

        with pytest.raises( InvalidTimeBlockException ):
            timeBlock.validate()

    '''
    Test for the toDict helper function
    '''
    def test_toDict( self ):
        expectedDict = {
            "start": datetime.time( 8, 0 ),
            "end": datetime.time( 19, 54 ),
            "mode": "MANUAL",
            "position": 52
        }
        
        timeBlock = ScheduleTimeBlock( expectedDict[ "start" ], expectedDict[ "end" ], BlindMode[ expectedDict[ "mode" ] ], expectedDict[ "position" ] )
        timeBlockDict = ScheduleTimeBlock.toDict( timeBlock )

        assert( timeBlockDict[ "start" ] == str( expectedDict[ "start" ] ) )
        assert( timeBlockDict[ "end" ] == str( expectedDict[ "end" ] ) )
        assert( timeBlockDict[ "mode" ] == expectedDict[ "mode" ] )
        assert( timeBlockDict[ "position" ] == expectedDict[ "position" ] )

    '''
    Test for fromDict with no errors
    '''
    def test_validFromDict( self ):
        timeBlockDict = {
            "start": "08:00:00",
            "end": "22:11:00",
            "mode": "MANUAL",
            "position": 52
        }

        expectedBlock = ScheduleTimeBlock( datetime.time( 8, 0 ), datetime.time( 22, 11 ), BlindMode.MANUAL, 52 )

        convertedBlock = ScheduleTimeBlock.fromDict( timeBlockDict )
        
        assert( convertedBlock == expectedBlock )

    '''
    Test for fromDict with invalid dictionary
    '''
    def test_invalidFromDict( self ):
        timeBlockDict = {
            "start": "08:00:00",
            "mode": "MANUAL",
            "position": 52
        }

        with pytest.raises( InvalidTimeBlockException ):
            convertedBlock = ScheduleTimeBlock.fromDict( timeBlockDict )

    '''
    Test for the toJson seralization function
    '''
    def test_serialize( self ):
        # expected json data for valid serialization
        validJson = '''{"start": "12:00:00", "end": "15:00:00", "mode": "MANUAL", "position": 52}'''
        timeBlock = ScheduleTimeBlock( datetime.time( 12, 0 ), datetime.time( 15, 0 ), BlindMode.MANUAL, 52 )

        assert( ScheduleTimeBlock.toJson( timeBlock ) == validJson )

    '''
    Test for fromJson deseralize with a valid json
    '''
    def test_validDeserialize( self ):
        validJson = '''{"start": "12:00:00", "end": "15:00:00", "mode": "MANUAL", "position": 52}'''
        timeBlock = ScheduleTimeBlock.fromJson( validJson )

        assert( timeBlock._start == datetime.time( 12, 0 ) )
        assert( timeBlock._end == datetime.time( 15, 0 ) )
        assert( timeBlock._mode == BlindMode.MANUAL )
        assert( timeBlock._position == 52 )

    '''
    Test for deseralize with an invalid json
    '''
    def test_invalidDeserialize( self ):
        invalidJson = '''{"start": "12:00:00", "end": "15:00:00", "mode": "MANUAL"}'''
        with pytest.raises( InvalidTimeBlockException ):
            timeBlock = ScheduleTimeBlock.fromJson( invalidJson )