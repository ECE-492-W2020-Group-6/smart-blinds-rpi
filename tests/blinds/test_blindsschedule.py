'''
Unit tests for the BlindsSchedule to verify the input validation and serialization.
Note that these tests assume the ScheduleTimeBlocks function correctly, as test_scheduletimeblock.py 
specifically tests that functionality. 

Author: Alex (Yin) Chen
Creation Date: February 23, 2020
'''

import pytest
import datetime
import json
import os
from blinds.blinds_schedule import BlindMode, ScheduleTimeBlock, BlindsSchedule, BlindSchedulingException, InvalidBlindsScheduleException
from pytz import timezone

# path used for opening json files
testFilePath = os.path.dirname( os.path.abspath( __file__ ) )

class TestScheduleTimeBlock:
    '''
    Test for constructor without errors. This also acts as a test for the validate function with 
    no errors
    '''
    def test_constructor( self ):
        default_mode = BlindMode.LIGHT
        default_pos = -45
        tz = timezone( "Etc/GMT-6" )
        sched = {
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
        }

        blindsSchedule = BlindsSchedule( default_mode, default_pos, sched, timezone=tz )
        assert( blindsSchedule._default_mode == default_mode )
        assert( blindsSchedule._default_pos == default_pos )
        assert( blindsSchedule._timezone.zone == tz.zone )

        for day in BlindsSchedule.DAYS_OF_WEEK:
            assert( len( blindsSchedule._schedule[ day ] ) == len( sched[ day ] ) )
            for block in blindsSchedule._schedule[ day ]:
                assert( block in sched[ day ] )

    '''
    Test for validate with invalid mode
    '''
    def test_invalidMode( self ):
        # initialize a valid BlindsSchedule
        default_mode = BlindMode.DARK
        sched = BlindsSchedule( default_mode )

        sched._default_mode = 2 # not a valid mode
        
        with pytest.raises( InvalidBlindsScheduleException ):
            sched.validate()

    '''
    Test for validate with BlindMode.MANUAL and invalid positions
    '''
    def test_invalidPosition( self ):
        # initialize a valid BlindsSchedule
        default_mode = BlindMode.DARK
        sched = BlindsSchedule( default_mode )

        sched._default_mode = BlindMode.MANUAL
        # default position is still None 
        with pytest.raises( InvalidBlindsScheduleException ):
            sched.validate()

        sched._default_pos = -300 # not in range [-100, 100]
        with pytest.raises( InvalidBlindsScheduleException ):
            sched.validate()

    '''
    Test for sorting a list of ScheduleTimeBlocks
    '''
    def test_sortedTimeBlockList( self ): 
        # empty list case, verify that it runs with no errors and returns the empty list 
        sortedList = BlindsSchedule.sortedTimeBlockList( [] )
        assert( not sortedList ) # this checks for result being an empty sequence

        timeBlockList = [ 
            ScheduleTimeBlock( datetime.time( 12, 00), datetime.time( 15, 00 ), BlindMode.LIGHT, None ),
            ScheduleTimeBlock( datetime.time( 4, 3), datetime.time( 6, 00 ), BlindMode.LIGHT, None ), 
            ScheduleTimeBlock( datetime.time( 22, 44), datetime.time(23, 00 ), BlindMode.LIGHT, None ), 
            ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.LIGHT, None ), 
            ScheduleTimeBlock( datetime.time( 10, 22), datetime.time( 12, 00 ), BlindMode.LIGHT, None ), 
            ScheduleTimeBlock( datetime.time( 00, 32), datetime.time( 1, 00 ), BlindMode.LIGHT, None )
        ]

        sortedList = BlindsSchedule.sortedTimeBlockList( timeBlockList )

        previousBlock = sortedList[ 0 ]
        for block in sortedList[ 1: ]:
            assert( previousBlock._start <= block._start )

    '''
    Test for time block list collision detection
    '''
    def test_hasConflict( self ):
        # lists must be sorted by start time 
        # list without conflict, should return False
        timeBlockList = [
            ScheduleTimeBlock( datetime.time( 4, 3), datetime.time( 6, 00 ), BlindMode.LIGHT, None ), 
            ScheduleTimeBlock( datetime.time( 12, 00), datetime.time( 15, 00 ), BlindMode.LIGHT, None ),
            ScheduleTimeBlock( datetime.time( 22, 44), datetime.time(23, 00 ), BlindMode.LIGHT, None ), 
        ]

        assert( BlindsSchedule.hasConflict( timeBlockList ) == False )

        # list with conflict, should return True
        timeBlockList = [
            ScheduleTimeBlock( datetime.time( 4, 3), datetime.time( 13, 00 ), BlindMode.LIGHT, None ), 
            ScheduleTimeBlock( datetime.time( 12, 00), datetime.time( 15, 00 ), BlindMode.LIGHT, None ),
            ScheduleTimeBlock( datetime.time( 22, 44), datetime.time(23, 00 ), BlindMode.LIGHT, None ), 
        ]

        assert( BlindsSchedule.hasConflict( timeBlockList ) == True )
    
    '''
    Test for time block conflict checking inside the BlindsSchedule object. This uses the BlindsSchedule.hasConflict function
    but will raise errors when appropriate. 
    '''
    def test_scheduleConflictChecks( self ):
        default_mode = BlindMode.LIGHT
        default_pos = -45

        blindsSchedule = BlindsSchedule( default_mode, default_pos )

        # start without conflict
        sched = {
            BlindsSchedule.SUNDAY: [],
            BlindsSchedule.MONDAY : [],
            BlindsSchedule.TUESDAY: [],
            BlindsSchedule.WEDNESDAY: [],
            BlindsSchedule.THURSDAY: [],
            BlindsSchedule.FRIDAY: [
                ScheduleTimeBlock( datetime.time( 00, 32), datetime.time( 6, 00 ), BlindMode.LIGHT, None ),
                ScheduleTimeBlock( datetime.time( 16, 44), datetime.time(23, 00 ), BlindMode.LIGHT, None ), 
                ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.ECO, None )
            ],
            BlindsSchedule.SATURDAY: []
        }

        blindsSchedule._schedule = sched
        assert( blindsSchedule.checkHasNoTimeConflicts() == True )

        # add time conflict
        sched = {
            BlindsSchedule.SUNDAY: [],
            BlindsSchedule.MONDAY : [],
            BlindsSchedule.TUESDAY: [],
            BlindsSchedule.WEDNESDAY: [],
            BlindsSchedule.THURSDAY: [],
            BlindsSchedule.FRIDAY: [
                ScheduleTimeBlock( datetime.time( 00, 32), datetime.time( 20, 00 ), BlindMode.LIGHT, None ),
                ScheduleTimeBlock( datetime.time( 16, 44), datetime.time(23, 00 ), BlindMode.LIGHT, None ), 
                ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.ECO, None )
            ],
            BlindsSchedule.SATURDAY: []
        }

        blindsSchedule._schedule = sched
        with pytest.raises( BlindSchedulingException ):
            blindsSchedule.checkHasNoTimeConflicts()

    '''
    Test for BlindSchedule serialization with toJson
    '''
    def test_serialization( self ):
        default_mode = BlindMode.LIGHT
        default_pos = None
        sched = {
            BlindsSchedule.SUNDAY: [
                ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.LIGHT, None ), 
                ScheduleTimeBlock( datetime.time( 5, 00), datetime.time( 7, 00 ), BlindMode.MANUAL, 15 )
            ],
            BlindsSchedule.MONDAY : [ 
                ScheduleTimeBlock( datetime.time( 12, 00), datetime.time( 15, 00 ), BlindMode.MANUAL, -33 ),
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
        }

        blindsSchedule = BlindsSchedule( default_mode, default_pos, sched )

        # use the sortKeys flag to allow deterministic output for comparison
        scheduleJson = BlindsSchedule.toJson( blindsSchedule, sortKeys=True )

        # open schedule1.json to compare 
        with open( os.path.join( testFilePath, "schedule1.json" ), "r" ) as file:
            expectedJson = file.read()

            assert( scheduleJson == expectedJson )

    '''
    Test parsing BlindsSchedule from Json with a valid JSON
    '''
    def test_validDeserialization( self ):
        default_mode = BlindMode.LIGHT
        default_pos = None
        sched = {
            BlindsSchedule.SUNDAY: [
                ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.LIGHT, None ), 
                ScheduleTimeBlock( datetime.time( 5, 00), datetime.time( 7, 00 ), BlindMode.MANUAL, 15 )
            ],
            BlindsSchedule.MONDAY : [ 
                ScheduleTimeBlock( datetime.time( 12, 00), datetime.time( 15, 00 ), BlindMode.MANUAL, -33 ),
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
        }

        expectedSched = BlindsSchedule( default_mode, default_pos, sched )

        with open( os.path.join( testFilePath, "schedule1.json" ), "r" ) as file:
            scheduleJson = file.read()

            parsedSched = BlindsSchedule.fromJson( scheduleJson )

            assert( parsedSched._default_mode == expectedSched._default_mode )
            assert( parsedSched._default_pos == expectedSched._default_pos )
            assert( parsedSched._schedule == expectedSched._schedule )
    
    '''
    Test parsing BlindsSchedule from Json with an invalid JSON
    '''
    def test_invalidDeserialization( self ):
        with open( os.path.join( testFilePath, "schedule2.json" ), "r" ) as file:
            scheduleJson = file.read()

            with pytest.raises( InvalidBlindsScheduleException ):
                parsedSched = BlindsSchedule.fromJson( scheduleJson )