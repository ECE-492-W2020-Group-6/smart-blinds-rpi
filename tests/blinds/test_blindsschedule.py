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
from blinds.blinds_schedule import BlindMode, ScheduleTimeBlock, BlindsSchedule, BlindSchedulingException, InvalidBlindsScheduleException

class TestScheduleTimeBlock:
    '''
    Test for constructor without errors
    '''
    def test_constructor( self ):
        default_mode = BlindMode.LIGHT
        default_pos = -45
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
                ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.GREEN, None ), 
                ScheduleTimeBlock( datetime.time( 00, 32), datetime.time( 1, 00 ), BlindMode.LIGHT, None )
            ],
            BlindsSchedule.SATURDAY: []
        }

        blindsSchedule = BlindsSchedule( default_mode, default_pos, sched )
        assert( blindsSchedule._default_mode == default_mode )
        assert( blindsSchedule._default_pos == default_pos )

        for day in BlindsSchedule.DAYS_OF_WEEK:
            assert( len( blindsSchedule._schedule[ day ] ) == len( sched[ day ] ) )
            for block in blindsSchedule._schedule[ day ]:
                assert( block in sched[ day ] )


