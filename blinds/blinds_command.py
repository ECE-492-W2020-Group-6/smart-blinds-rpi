'''
File for blinds command related code. Commands are manual actions set by the user that are sent from the external application. 
These classes aim to model the command to more easily interact with the API. 
Contains classes: 


Also contains custom exception classes to provide more specific exceptions for commands. 
Currently, these are: 


Author: Alex (Yin) Chen
Creation Date: March 6, 2020
'''
import json
import datetime 
from blinds.blinds_schedule import BlindMode, ScheduleTimeBlock

'''
Class to model the commands sent from the external app to control the blinds. These will generally fall into the form 
of having a desired mode(from BlindMode), duration(in minutes), and position. Giving a duration of 0 will set the blinds
to the given state until the end of the day. Commands with durations going beyond the end of the day will be truncated to
end at the end of the day, returning to the scheduled behaviour. 

This class acts as an intermediate step before creating a schedule time block to represent the state. 
'''
class BlindsCommand:
    _mode = None
    _position = None
    _duration = None

    '''
    Constructor. Initializes a BlindsCommand object with mode and duration. Position is required only for BlindMode.MANUAL. 
    Validation is performed at the end to ensure that the generated object is valid. 
    '''
    def __init__( self, mode, duration, position=None ):
        self._mode = mode
        self._duration = duration
        self._position = position

        self.validate()

    def validate( self ):
        if not isinstance( self._mode, BlindMode ):
            raise InvalidBlindsCommandException( "mode must be a value from the BlindMode enum" )
        
        if self._mode == BlindMode.MANUAL and self._position is None: 
            raise InvalidBlindsCommandException( "position must be specified when using BlindMode.MANUAL" )
        elif self._mode == BlindMode.MANUAL and ( self._position > 100 or self._position < -100 ):
            raise InvalidBlindsCommandException( "position must a value from -100 to 100" )

        if self._duration < 0: 
            raise InvalidBlindsCommandException( "duration must be at least 1(minute)")

        return True

    '''
    Converts the BlindsCommand into a corresponding ScheduleTimeBlock beginning at the current time and lasting for the provided 
    duration.

    currentTimeProvider is a parameterless function that gives the current time. This can be used to force a certain way of 
    retrieving the time for tests or other implementations. Otherwise, if not provided, the datetime.utcnow() function will 
    be used to get the current time. The time should be a datetime.time object with hours and minutes defined. The seconds and
    milliseconds will be ignored.

    Returns the schedule time block starting from the current time, and ending self._duration minutes later (except when duration
    is 0), or at the end of the day if duration is 0 or longer than the time remaining in the day    
    '''
    def toTimeBlock( self, currentTimeProvider=None ): 
        if currentTimeProvider is None:
            currentTime = datetime.datetime.utcnow().time()
        else:
            currentTime = currentTimeProvider()
        startTime = datetime.time( currentTime.hour, currentTime.minute )

        if ( self._duration == 0 ):
            endTime = ScheduleTimeBlock.END_OF_DAY
        else:
            # convert duration in minutes to hours + minutes
            hourOffset = int( ( currentTime.minute + self._duration ) / 60 ) 
            newHour = currentTime.hour + hourOffset
            newMinutes = ( currentTime.minute + self._duration ) % 60

            if ( newHour > 23 ):
                endTime = ScheduleTimeBlock.END_OF_DAY
            else:
                endTime = datetime.time( newHour, newMinutes )
        
        # check edge case of start and end at 23:59, which will be only case of true 0 duration
        # this will cause errors in the time block. In this case, there is 0 duration and thus no 
        # real time block, so we return None for consistency
        if ( startTime == endTime ):
            return None

        return ScheduleTimeBlock( startTime, endTime, self._mode, self._position )
        

    # ---------- Static Helper Methods for Serialization/Deserialization --------- #
    @staticmethod
    def toDict( command ):
        commandDict = dict()
        commandDict[ "mode" ] = command._mode.name
        commandDict[ "position" ] = command._position
        commandDict[ "duration" ] = command._duration

        return commandDict

    @staticmethod
    def fromDict( commandDict ):
        print( commandDict ) 
        try:
            return BlindsCommand( BlindMode[ commandDict[ "mode" ] ], commandDict[ "duration" ], commandDict[ "position" ] )
        
        except KeyError as err:
            raise InvalidBlindsCommandException( "Missing key when parsing command: " + str( err ) )

    @staticmethod
    def toJson( command, pretty=False, sortKeys=False ):
        if pretty:
            return json.dumps( BlindsCommand.toDict( command ), sort_keys=sortKeys, indent=4 )

        return json.dumps( BlindsCommand.toDict( command ), sort_keys=sortKeys )

    @staticmethod
    def fromJson( commandJson ):
        return BlindsCommand.fromDict( json.loads( commandJson ) )


    # ---------- End of Static Methods for Serialization/Deserialization --------- #

# ---------- Custom Exception classes --------- #
# Thrown when the BlindsCommand object is invalid
class InvalidBlindsCommandException( Exception ):
    pass
# ---------- END OF Custom Exception classes --------- #
