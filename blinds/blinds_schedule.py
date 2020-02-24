'''
File for blinds schedule related code. 
Contains classes: 
    BlindMode( Enum ): Enum type to represent the mode of the blinds during a given time block
    ScheduleTimeBlock: class to represent a time block and the associated state of the blinds during that time
    BlindsSchedule: class to hold the scheduling mechanism, gives functions for serializaion and deserialization

Also contains custom exception classes to provide more specific exceptions for scheduling. 
Currently, these are: 
    InvalidBlindsScheduleException
    BlindSchedulingException
    InvalidTimeBlockException

Note, the API handlers are not implemented, and the dummy data there is used to indicate the intended format of 
the response data. 

Author: Alex (Yin) Chen
Creation Date: February 19, 2020
'''

from enum import Enum
import json
import datetime 

'''
Enum type for blind mode.
'''
class BlindMode( Enum ):
    LIGHT = 1
    DARK = 2 
    GREEN = 3
    MANUAL = 4    

'''
Class represeting the time block elements for the schedule
'''
class ScheduleTimeBlock:
    _start = None
    _end = None 
    _mode = None
    _position = None
    
    '''
    Constructor for ScheduleTimeBlock. Sets the values for the time block and the state of the blinds during it. 
    Validates the object after the sets. 
    
    Arguments:
    start - a datetime.time object
    end - a datetime.time object
    mode - a value from BlindMode

    Keyword arguments:
    position - a valid blind position, required if mode is manual but optional otherwise
    '''
    def __init__( self, start, end, mode, position=None ):
        self._start = start
        self._end = end
        self._mode = mode
        self._position = position

        self.validate()

    '''
    Update function for changing internal values of a ScheduleTimeBlock. Also calls the 
    validate function to ensure that the object remains valid. 
    '''
    def update( self, start=None, end=None, mode=None, position=None ):
        if start is not None: 
            self._start = start
        if end is not None: 
            self._end = end
        if mode is not None: 
            self._mode = mode 

        # no check for position because it is not necessary for all modes
        # however if the mode requires it, it will throw an error in validate if the position is not set. 
        # setting position to None when not given results in more consistent behaviour.
        self._position = position

        self.validate()

    # ---------- Static Methods for Serialization/Deserialization --------- #
    '''
    Serialize the time block to JSON format. This is done by generating a dictionary for the json.
    TODO: Comment
    '''
    @staticmethod
    def toJson( timeBlock ):
        if timeBlock is None: 
            return "{}"

        jsonDict = dict()
        jsonDict[ "start" ] = str( timeBlock._start )
        jsonDict[ "end" ] = str( timeBlock._end )
        jsonDict[ "mode" ] = timeBlock._mode.name # get the name of the mode, rather than the ENUM value
        jsonDict[ "position" ] = timeBlock._position 

        return json.dumps( jsonDict )

    '''
    Deserializes the jsonStr into a ScheduleTimeBlock object. Calls validate on the generated ScheduleTimeBlock.
    
    '''
    @staticmethod
    def fromJson( jsonStr ):
        jsonDict = json.loads( jsonStr )

        # produce more descriptive error for missing keys 
        try:
            # temporary variable used for splitting the time string so we can create a proper datetime object
            tempTimeList = jsonDict[ "start" ].split( ":" )

            # 0 is index of hour, 1 is index of minute, we ignore seconds
            startTime = datetime.time( int( tempTimeList[ 0 ] ), int( tempTimeList[ 1 ] ) )

            tempTimeList = jsonDict[ "end" ].split( ":" )
            endTime = datetime.time( int( tempTimeList[ 0 ] ), int( tempTimeList[ 1 ] ) )

            return ScheduleTimeBlock( startTime, endTime, BlindMode[ jsonDict[ "mode" ] ], jsonDict[ "position" ] )

        except KeyError as keyError:
            raise InvalidTimeBlockException( "Missing key in ScheduleTimeBlock json: " + str( keyError ) )
        

    # ---------- End of Static Methods for Serialization/Deserialization --------- #


    '''
    Validates the contents of a schedule time block. Returns true when the time block is valid,
    throws InvalidTimeBlockException when invalid. 
    Invalid blocks are blocks where the start time <= end time, or when the mode is BlindMode.manual without setting a position.
    '''
    def validate( self ): 
        if not ( isinstance( self._start, datetime.time ) and isinstance( self._start, datetime.time ) ):
            raise InvalidTimeBlockException( "start and end times must be instances of datetime.time")

        if self._start >= self._end:
            raise InvalidTimeBlockException( "start time must be before the end time")

        if not isinstance( self._mode, BlindMode ):
            raise InvalidTimeBlockException( "mode must be a value from the BlindMode enum" )

        if self._mode == BlindMode.MANUAL and self._position is None: 
            raise InvalidTimeBlockException( "position must be specified when using BlindMode.MANUAL" )
        elif self._mode == BlindMode.MANUAL and ( self._position > 100 or self._position < -100 ):
            raise InvalidTimeBlockException( "position must a value from -100 to 100" )

        return True

'''
Class for handling blinds scheduling to define a 
structure for the schedule and editing functionlity.

Provides functions to serialize and deserialize a BlindsSchedule

Schedule formatted as having a default state or behavior, then with a dictionary of 
days of the week mapping to an array of ScheduleTimeBlocks that define the blinds' state 
during that time. That is, the time blocks define behavior differing from the default
during the specified time block

The general format is: 
{
    "default_mode": one of {"LIGHT", "DARK", "GREEN", "MANUAL"},
    "default_pos" [required only for default="custom"] : <int> position,
    "schedule": {
        "sunday": [ <time block 1>, <time block 2>, ... ],
        "monday": [ <time block 1>, <time block 2>, ... ],
        "tuesday": [ <time block 1>, <time block 2>, ... ],
        "wednesday": [ <time block 1>, <time block 2>, ... ],
        "thursday": [ <time block 1>, <time block 2>, ... ],
        "friday": [ <time block 1>, <time block 2>, ... ],
        "saturday": [ <time block 1>, <time block 2>, ... ]
    }
}
'''
class BlindsSchedule:
    # class constants for days of the week
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"

    DAYS_OF_WEEK = set( [ SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY ] )

    _default_mode = None 
    _default_pos = None
    _schedule = {
        SUNDAY : [],
        MONDAY : [],
        TUESDAY : [],
        WEDNESDAY : [],
        THURSDAY : [],
        FRIDAY : [],
        SATURDAY : []
    }

    def __init__( self, default_mode, default_pos=None, schedule=None ):
        self._default_mode = default_mode
        self._default_pos = default_pos

        if schedule is not None:
            self._schedule = schedule
            self.sortScheduleBlocks()

    def sortScheduleBlocks( self ):
        for day in DAYS_OF_WEEK:
            self._schedule[ day ] = sortedTimeBlockList( self._schedule[ day ] )

    def validate( self ):
        # checks for default mode and position
        if not isinstance( self._default_mode, BlindMode ): 
            raise InvalidBlindsScheduleException( "default mode must be a value from the BlindMode enum" )

        if self._default_mode == BlindMode.MANUAL and self._position is None: 
            raise InvalidBlindsScheduleException( "default position must be specified when using BlindMode.MANUAL" )
        elif self._default_mode == BlindMode.MANUAL and ( self._position > 100 or self._position < -100 ):
            raise InvalidBlindsScheduleException( "default position must a value from -100 to 100" )

        # checks for _schedule being well formatted
        if not isinstance( self._schedule, dict ) or ( self._schedule.keys != DAYS_OF_WEEK ):
            raise InvalidBlindsScheduleException( "schedule must be a dictionary with keys being the days of the week and values being lists of ScheduleTimeBlocks" )
        
        for day in DAYS_OF_WEEK:
            timeBlockList = self._schedule[ day ]
            if not all( map( lambda x: isinstance( x, ScheduleTimeBlock ), timeBlockList ) ):
                raise InvalidBlindsScheduleException( "schedule must be a dictionary with keys being the days of the week and values being lists of ScheduleTimeBlocks" )
            
            # checks for time conflicts
            if BlindsSchedule.hasConflict( timeBlockList ):
                raise BlindsSchedulingException( "schedule has conflicting time blocks on " + day )

        return True

    def serialize( self ): 
        raise NotImplementedError

    def deserialize( self ): 
        raise NotImplementedError

    '''
    Returns a list of ScheduleTimeBlocks sorted by start times. Does NOT check for time conflicts.
    Assumes that all the time blocks are valid. 
    '''
    @staticmethod
    def sortedTimeBlockList( timeBlockList ):
        return sorted( timeBlockList, key= lambda x : x._start )

    '''
    Checks for time block conflicts given a list of ScheduleTimeBlocks sorted by start time.
    A time conflict is defined as having time blocks with overlapping durations.
    Assumes that all the time blocks are valid. 

    Returns True if there is a conflict, false otherwise. 
    '''
    @staticmethod
    def hasConflict( timeBlockList ): 
        lastTimeBlock = None
        for timeBlock in timeBlockList: 
            print( "last: ", ScheduleTimeBlock.toJson( lastTimeBlock ))
            print( "now: ", ScheduleTimeBlock.toJson( timeBlock ))


            if lastTimeBlock is not None and timeBlock._start < lastTimeBlock._end:
                return True
            lastTimeBlock = timeBlock

        return False
    


# ---------- Custom Exception classes --------- #
# Thrown when the BlindsSchedule object is invalid
class InvalidBlindsScheduleException( Exception ):
    pass

# Thrown when there are conflicting time blocks in a BlindSchedule
class BlindSchedulingException( Exception ):
    pass

# Thrown when a time block is improperly set
class InvalidTimeBlockException( Exception ):
    pass
# ---------- END OF Custom Exception classes --------- #


b = [ ScheduleTimeBlock( datetime.time( 12, 00), datetime.time( 15, 00 ), BlindMode.LIGHT, None ),
    ScheduleTimeBlock( datetime.time( 4, 3), datetime.time( 6, 00 ), BlindMode.LIGHT, None ), 
    ScheduleTimeBlock( datetime.time( 22, 44), datetime.time(23, 00 ), BlindMode.LIGHT, None ), 
    ScheduleTimeBlock( datetime.time( 23, 38), datetime.time( 23, 59 ), BlindMode.LIGHT, None ), 
    ScheduleTimeBlock( datetime.time( 10, 22), datetime.time( 12, 00 ), BlindMode.LIGHT, None ), 
    ScheduleTimeBlock( datetime.time( 00, 32), datetime.time( 1, 00 ), BlindMode.LIGHT, None ) ]

sorted_b = BlindsSchedule.sortedTimeBlockList( b )

for t in sorted_b:
    print( ScheduleTimeBlock.toJson( t ) )

print( BlindsSchedule.hasConflict( sorted_b ) )
print( BlindsSchedule.sortedTimeBlockList([]) )

# x = ScheduleTimeBlock.toJson( b ) 
# print(x)
# y = ScheduleTimeBlock.fromJson( x )
# print( y == b )
# print( b.__dict__ )
# print( y.__dict__) 