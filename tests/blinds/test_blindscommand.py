'''
Unit tests for the BlindsCommand to verify the input validation and serialization

Author: Alex (Yin) Chen
Creation Date: March 7, 2020
'''

import pytest
import json
import datetime
from blinds.blinds_schedule import BlindMode, ScheduleTimeBlock
from blinds.blinds_command import BlindsCommand, InvalidBlindsCommandException

class TestBlindsCommand:
    '''
    Test for constructor and basic validate with no errors
    '''
    def test_constructor( self ):
        # test without the position parameter
        command = BlindsCommand( BlindMode.DARK, 30 )
        assert( command._mode == BlindMode.DARK )
        assert( command._duration == 30 )
        assert( command._position == None )

        # Test constructor with manual mode and position 
        command = BlindsCommand( BlindMode.MANUAL, 10, 70 )
        assert( command._mode == BlindMode.MANUAL )
        assert( command._duration == 10 )
        assert( command._position == 70 )

    '''
    Test for validate with invalid mode
    '''
    def test_invalidMode( self ): 
        # start with a valid Command
        command = BlindsCommand( BlindMode.MANUAL, 10, 70 )

        # manually update command to invalid mode
        command._mode = "NOT_A_MODE"
        
        with pytest.raises( InvalidBlindsCommandException ):
            command.validate()
    
    '''
    Test for validate with invalid duration
    '''
    def test_invalidDuration( self ): 
        # start with a valid Command
        command = BlindsCommand( BlindMode.MANUAL, 10, 70 )

        # manually update duration to invalid value
        command._duration = -1
        
        with pytest.raises( InvalidBlindsCommandException ):
            command.validate()

    '''
    Test for validate with missing position
    '''
    def test_missingPos( self ): 
        # start with a valid Command
        command = BlindsCommand( BlindMode.MANUAL, 10, 70 )
        command._position = None
        
        with pytest.raises( InvalidBlindsCommandException ):
            command.validate()

    '''
    Test for validate with invalid position
    '''
    def test_invalidDuration( self ): 
        # start with a valid Command
        command = BlindsCommand( BlindMode.MANUAL, 10, 70 )

        # manually update position to invalid value
        command._position = -500
        
        with pytest.raises( InvalidBlindsCommandException ):
            command.validate()

    '''
    Tests for converting command to a scheduletime block 
    '''
    def test_toScheduleTimeBlock( self ): 
        mockHour = 16
        mockMinute = 31
        mockCurrentTime = lambda: datetime.time( mockHour, mockMinute )

        commandMode = BlindMode.MANUAL
        commandPos = 70
        # command for 2 hours
        commandTime = 120
        command = BlindsCommand( commandMode, commandTime, commandPos )
        timeBlock = command.toTimeBlock( currentTimeProvider=mockCurrentTime )

        assert( timeBlock._start.hour == mockHour )
        assert( timeBlock._start.minute == mockMinute )
        assert( timeBlock._end.hour == mockHour + 2 )
        assert( timeBlock._end.minute == mockMinute )

        # command for 2 hours and 10 minutes
        commandTime = 130
        command = BlindsCommand( commandMode, commandTime, commandPos )
        timeBlock = command.toTimeBlock( currentTimeProvider=mockCurrentTime )

        assert( timeBlock._start.hour == mockHour )
        assert( timeBlock._start.minute == mockMinute )
        assert( timeBlock._end.hour == mockHour + 2 )
        assert( timeBlock._end.minute == mockMinute + 10 )

        # case of end of day with duration = 0
        commandTime = 0
        command = BlindsCommand( commandMode, commandTime, commandPos )
        timeBlock = command.toTimeBlock( currentTimeProvider=mockCurrentTime )

        assert( timeBlock._start.hour == mockHour )
        assert( timeBlock._start.minute == mockMinute )
        assert( timeBlock._end.hour == ScheduleTimeBlock.END_OF_DAY.hour )
        assert( timeBlock._end.minute == ScheduleTimeBlock.END_OF_DAY.minute )

        # case of end of day with duration too long
        commandTime = 6000
        command = BlindsCommand( commandMode, commandTime, commandPos )
        timeBlock = command.toTimeBlock( currentTimeProvider=mockCurrentTime )

        assert( timeBlock._start.hour == mockHour )
        assert( timeBlock._start.minute == mockMinute )
        assert( timeBlock._end.hour == ScheduleTimeBlock.END_OF_DAY.hour )
        assert( timeBlock._end.minute == ScheduleTimeBlock.END_OF_DAY.minute )

        # case of true 0 duration with various command times
        mockCurrentTime = lambda: ScheduleTimeBlock.END_OF_DAY

        # arbitrary command time
        command = BlindsCommand( commandMode, 120, commandPos )
        timeBlock = command.toTimeBlock( currentTimeProvider=mockCurrentTime )
        assert( timeBlock is None )

        # 0 command time
        command = BlindsCommand( commandMode, 0, commandPos )
        timeBlock = command.toTimeBlock( currentTimeProvider=mockCurrentTime )
        assert( timeBlock is None )

        # command time too long
        command = BlindsCommand( commandMode, 6000, commandPos )
        timeBlock = command.toTimeBlock( currentTimeProvider=mockCurrentTime )
        assert( timeBlock is None )

    '''
    Test toDict function 
    '''
    def test_toDict( self ):
        command = BlindsCommand( BlindMode.MANUAL, 10, 70 )
        commandDict = BlindsCommand.toDict( command )

        assert( commandDict[ "mode" ] == command._mode.name )
        assert( commandDict[ "duration" ] == command._duration )
        assert( commandDict[ "position" ] == command._position )

    '''
    Test fromDict function with a valid dictionary
    '''
    def test_validFromDict( self ): 
        commandDict = {
            "mode": BlindMode.DARK.name,
            "duration": 20, 
            "position": None
        }

        command = BlindsCommand.fromDict( commandDict )

        assert( command._mode.name == commandDict[ "mode" ] )
        assert( command._duration == commandDict[ "duration" ] )
        assert( command._position == commandDict[ "position" ] )

    '''
    Test fromDict function with an invalid dictionary
    '''
    def test_invalidFromDict( self ): 
        commandDict = {
            "not": "abc",
            "valid": 123,
            "dictionary": {}
        }

        with pytest.raises( InvalidBlindsCommandException ):
            command = BlindsCommand.fromDict( commandDict )

    '''
    Test toJson serialization function
    '''
    def test_toJson( self ):
        command = BlindsCommand( BlindMode.MANUAL, 20, -32 )

        # use expected json with sorted keys to ensure result is deterministic, though 
        # this is likely not necessary due to the simplicity of the structure
        expectedJson = '{"duration": 20, "mode": "MANUAL", "position": -32}'

        assert( BlindsCommand.toJson( command, sortKeys=True ) == expectedJson )

    '''
    Test fromJson deserialization function with a valid json
    '''
    def test_validFromJson( self ): 
        validJson = '{"duration": 20, "mode": "MANUAL", "position": -32}'
        expectedCommand = BlindsCommand( BlindMode.MANUAL, 20, -32 )

        parsedCommand = BlindsCommand.fromJson( validJson )

        assert( parsedCommand._mode == expectedCommand._mode )
        assert( parsedCommand._position == expectedCommand._position )
        assert( parsedCommand._duration == expectedCommand._duration )

    '''
    Test fromJson deserialize function with an invalid json 
    '''
    def test_invalidFromJson( self ): 
        invalidJson = '{"abc": 123, "def": "567", "qwerty": -1}'

        with pytest.raises( InvalidBlindsCommandException ):
            parsedCommand = BlindsCommand.fromJson( invalidJson )