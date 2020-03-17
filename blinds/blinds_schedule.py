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
This is used to ensure consistent values for the mode. 
    LIGHT : Maximum sunlight
    DARK : Closed, minimum sunlight
    ECO : Energy efficiency mode
    MANUAL : Set custom position
'''
class BlindMode( Enum ):
    LIGHT = 1
    DARK = 2 
    ECO = 3
    MANUAL = 4    

'''
Class represeting the time block elements for the schedule. Contains a dictionary schedule mapping days of the week
to a list of time blocks for that day. 
A schedule consists of a default mode and position, indicating the state in which the blinds should take when there is no
specified time block. Thus, time blocks constitute exceptions to the default. 
'''
class ScheduleTimeBlock:
    # public attributes
    # static constant for end of day 
    END_OF_DAY = datetime.time( 23, 59 )

    # private atttributes
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

    # ---------- Static Helper Methods for Serialization/Deserialization --------- #
    '''
    Converts a ScheduleTimeBlock into a dictionary that can be easily translated to JSON. 
    This is also called by the BlindsSchedule toJson function in order to keep the time blocks as dictionaries rather 
    than converting to escaped strings. 
    '''
    @staticmethod
    def toDict( timeBlock ):
        if timeBlock is None: 
            return "{}"

        jsonDict = dict()
        jsonDict[ "start" ] = str( timeBlock._start )
        jsonDict[ "end" ] = str( timeBlock._end )
        jsonDict[ "mode" ] = timeBlock._mode.name # get the name of the mode, rather than the ENUM value
        jsonDict[ "position" ] = timeBlock._position 

        return jsonDict

    '''
    Converts a dictionary into a ScheduleTimeBlock object.
    Missing keys will raise InvalidTimeBlockException, otherwise the new ScheduleTimeBlock object will be returned. 
    The generated ScheduleTimeBlock will be validated during creation.
    '''
    @staticmethod
    def fromDict( timeBlockDict ):
        # produce more descriptive error for missing keys 
        try:
            # temporary variable used for splitting the time string so we can create a proper datetime object
            tempTimeList = timeBlockDict[ "start" ].split( ":" )

            # 0 is index of hour, 1 is index of minute, we ignore seconds
            startTime = datetime.time( int( tempTimeList[ 0 ] ), int( tempTimeList[ 1 ] ) )

            tempTimeList = timeBlockDict[ "end" ].split( ":" )
            endTime = datetime.time( int( tempTimeList[ 0 ] ), int( tempTimeList[ 1 ] ) )

            return ScheduleTimeBlock( startTime, endTime, BlindMode[ timeBlockDict[ "mode" ] ], timeBlockDict[ "position" ] )

        except KeyError as keyError:
            raise InvalidTimeBlockException( "Missing key in ScheduleTimeBlock json: " + str( keyError ) )

    '''
    Serialize the time block to JSON format. This is done by first generating a dictionary for the json.
    Returns the json dump for the dictionary generated from toDict
    '''
    @staticmethod
    def toJson( timeBlock ):
        return json.dumps( ScheduleTimeBlock.toDict( timeBlock ) )

    '''
    Deserializes the json string into a ScheduleTimeBlock object by first converting it into a dictionary and calling fromDict    
    '''
    @staticmethod
    def fromJson( jsonStr ):
        jsonDict = json.loads( jsonStr )

        return ScheduleTimeBlock.fromDict( jsonDict )

    # ---------- End of Static Methods for Serialization/Deserialization --------- #


    '''
    Validates the contents of a schedule time block. Returns true when the time block is valid,
    throws InvalidTimeBlockException when invalid. 
    Invalid blocks are blocks where the start time <= end time, or when the mode is BlindMode.manual without setting a position.
    '''
    def validate( self ): 
        if not ( isinstance( self._start, datetime.time ) and isinstance( self._start, datetime.time ) ):
            raise InvalidTimeBlockException( "start=%s, end=%s start and end times must be instances of datetime.time" % ( self._start, self._end ) )

        if self._start >= self._end:
            raise InvalidTimeBlockException( "start=%s, end=%s start time must be before the end time" % ( self._start, self._end ) )

        if not isinstance( self._mode, BlindMode ):
            raise InvalidTimeBlockException( "mode must be a value from the BlindMode enum" )

        if self._mode == BlindMode.MANUAL and self._position is None: 
            raise InvalidTimeBlockException( "position must be specified when using BlindMode.MANUAL" )
        elif self._mode == BlindMode.MANUAL and ( self._position > 100 or self._position < -100 ):
            raise InvalidTimeBlockException( "position must a value from -100 to 100" )

        return True

    '''
    Returns whether or not the ScheduleTimeBlock is equal to other. 
    Override default equality check to check internal values of the ScheduleTimeBlock instead of the object identifier.
    '''
    def __eq__( self, other ):
        if not isinstance( other, ScheduleTimeBlock ):
            return False
        else:
            return self._start == other._start and self._end == other._end and self._mode == other._mode and self._position == other._position 

'''
Class for handling blinds scheduling to define a 
structure for the schedule and editing functionlity.

Provides functions to serialize and deserialize a BlindsSchedule

Schedule formatted as having a default state or behavior, then with a dictionary of 
days of the week mapping to an array of ScheduleTimeBlocks that define the blinds' state 
during that time. That is, the time blocks define behavior differing from the default
during the specified time block

The general json format is: 
{
    "default_mode": one of {"LIGHT", "DARK", "ECO", "MANUAL"},
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
    # class constants for days of the week, these values should NOT be changed
    SUNDAY = "sunday"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"

    DAYS_OF_WEEK = set( [ SUNDAY, MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY ] )

    # object attributes describing the schedule
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

    '''
    Constructor for BlindsSchedule. Initializes it with the default mode and position, and a 
    schedule of time blocks if provided. 
    Calls self.validate at the end to ensure that the created object is valid.
    The schedule is also sorted and checked for conflicts.  
    '''
    def __init__( self, default_mode, default_pos=None, schedule=None ):
        self._default_mode = default_mode
        self._default_pos = default_pos

        if schedule is not None:
            self._schedule = schedule

        # validate and checking for conflicts are separated to ensure that the time blocks can be sorted without error
        self.validate()
        self.sortScheduleBlocks()
        self.checkHasNoTimeConflicts()

    def sortScheduleBlocks( self ):
        for day in BlindsSchedule.DAYS_OF_WEEK:
            self._schedule[ day ] = BlindsSchedule.sortedTimeBlockList( self._schedule[ day ] )

    '''
    Validates the BlindsSchedule object. Returns True if the BlindsSchedule is properly defined, and throws exceptions otherwise. 
    InvalidBlindsScheduleException is thrown when the parameters of the object itself are invalid, such as 
    having an improperly defined schedule or improperly set default behaviour. 

    The validation assumes that the ScheduleTimeBlocks themselves are valid, as these should be validated upon their
    creation and update and thus should be valid by the time they are using in the BlindsSchedule object. This is a 
    conscious choice to improve performace of the validate calls. 

    Does NOT check for time conflicts
    '''
    def validate( self ):
        # checks for default mode and position
        if not isinstance( self._default_mode, BlindMode ): 
            raise InvalidBlindsScheduleException( "default mode must be a value from the BlindMode enum" )

        if self._default_mode == BlindMode.MANUAL and self._default_pos is None: 
            raise InvalidBlindsScheduleException( "default position must be specified when using BlindMode.MANUAL" )
        elif self._default_mode == BlindMode.MANUAL and ( self._default_pos > 100 or self._default_pos < -100 ):
            raise InvalidBlindsScheduleException( "default position must a value from -100 to 100" )

        # checks for _schedule being well formatted
        if not isinstance( self._schedule, dict ) or ( set( self._schedule.keys() ) != BlindsSchedule.DAYS_OF_WEEK ):
            raise InvalidBlindsScheduleException( "schedule must be a dictionary with keys being the days of the week and values being lists of ScheduleTimeBlocks" )
        
        for day in BlindsSchedule.DAYS_OF_WEEK:
            timeBlockList = self._schedule[ day ]
            if not all( map( lambda x: isinstance( x, ScheduleTimeBlock ), timeBlockList ) ):
                raise InvalidBlindsScheduleException( "schedule must be a dictionary with keys being the days of the week and values being lists of ScheduleTimeBlocks" )

        return True

    '''
    Checks for scheduling conflicts within a BlindsSchedule object. 
    Will raise BlindSchedulingException when there conflicting time blocks on a given day. 
    The should only be called after the time blocks for each day are sorted. 
    Otherwise, returns True when there are no conflicts. 
    '''
    def checkHasNoTimeConflicts( self ):
        for day in BlindsSchedule.DAYS_OF_WEEK: 
            # checks for time conflicts
            if BlindsSchedule.hasConflict( self._schedule[ day ] ):
                raise BlindSchedulingException( "schedule has conflicting time blocks on " + day )

        return True

    '''
    Returns timeBlockList of ScheduleTimeBlocks sorted by start times. Does NOT check for time conflicts.
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
            if lastTimeBlock is not None and timeBlock._start < lastTimeBlock._end:
                return True
            lastTimeBlock = timeBlock

        return False

    '''
    Returns a JSON-like dictionary representation of the BlindsSchedule object.
    '''
    @staticmethod
    def toDict( schedule ):
        jsonDict = dict()
        if schedule is not None: 
            jsonDict[ "default_mode" ] = schedule._default_mode.name 

            jsonDict[ "default_pos" ] = schedule._default_pos
            
            jsonDict[ "schedule" ] = dict() 
            for day in BlindsSchedule.DAYS_OF_WEEK: 
                jsonDict[ "schedule" ][ day ] = list( map( lambda x : ScheduleTimeBlock.toDict( x ), schedule._schedule[ day ] ) )

        return jsonDict

    '''
    Returns a BlindsSchedule object based on the provided JSON-like dictionary. 
    Raises InvalidBlindsScheduleException for missing keys.
    '''
    @staticmethod
    def fromDict( jsonDict ):
        try:
            default_mode = BlindMode[ jsonDict[ "default_mode" ] ]
            default_pos = jsonDict[ "default_pos" ]
            # account for integer casee
            if default_pos is not None: 
                default_pos = int( default_pos )

            parsed_sched = jsonDict[ "schedule" ]

            blindsSchedule = BlindsSchedule( default_mode, default_pos )
            for day in BlindsSchedule.DAYS_OF_WEEK:
                blindsSchedule._schedule[ day ] = list( map( lambda x: ScheduleTimeBlock.fromDict( x ), parsed_sched[ day ] ) )

            blindsSchedule.validate()
            blindsSchedule.sortScheduleBlocks()
            blindsSchedule.checkHasNoTimeConflicts()

            return blindsSchedule

        except KeyError as error:
            raise InvalidBlindsScheduleException( "Missing key in json: " + str( error ) ) 

    '''
    Returns a JSON representation of a valid BlindsSchedule object.
    Provides additional keyword arguments for pretty printing and sorting the json output's keys. 
    '''
    @staticmethod
    def toJson( schedule, pretty=False, sortKeys=False ): 
        if pretty:
            return json.dumps( BlindsSchedule.toDict( schedule ), sort_keys=sortKeys, indent=4 )
        else:
            return json.dumps( BlindsSchedule.toDict( schedule ), sort_keys=sortKeys )

    '''
    Parses a json representation of the the schedule and returns a new BlindsSchedule object. 
    Raises InvalidBlindsScheduleException for missing keys in the JSON string. 
    '''
    @staticmethod
    def fromJson( scheduleJson ): 
        parsedDict = json.loads( scheduleJson )

        return BlindsSchedule.fromDict( parsedDict )

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