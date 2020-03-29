'''
Unit tests for the Blinds object from blinds/blinds_api
Focus of the tests is on the internals of the Blinds object itself, without the dependencies on the 
motor driver or other external modules. 

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''

import pytest
from blinds.blinds_api import Blinds, InvalidBlindPositionException
from controlalgorithm.angle_step_mapper import AngleStepMapper

class TestBlinds:

    '''
    Test rotateToPosition to check that the internal position is updated. 
    '''
    def test_rotate( self ):
        mapper = AngleStepMapper()
        blinds = Blinds( None, mapper )
        
        assert ( blinds._currentPosition == 0 )

        blinds.rotateToPosition( 12 )
        assert ( blinds._currentPosition == 12 )

        blinds.rotateToPosition( 100 )
        assert ( blinds._currentPosition == 100 )

        blinds.rotateToPosition( -54 )
        assert ( blinds._currentPosition == -54 )

        blinds.rotateToPosition( -100 )
        assert ( blinds._currentPosition == -100 )

    '''
    Test for invalid rotational positions given to rotateToPosition. 
    These are expected to throw InvalidBlindPositionException
    '''
    def test_invalid_rotation( self ):
        blinds = Blinds( None, None )
        with pytest.raises( InvalidBlindPositionException ):
            blinds.rotateToPosition( 101 )

        with pytest.raises( InvalidBlindPositionException ):
            blinds.rotateToPosition( 500 )
        
        with pytest.raises( InvalidBlindPositionException ):
            blinds.rotateToPosition( -101 )

        with pytest.raises( InvalidBlindPositionException ):
            blinds.rotateToPosition( -500 )

    '''
    Test for resetPosition. Checks that the internal position was reset to 0. 
    '''
    def test_reset_position( self ):
        mapper = AngleStepMapper()
        blinds = Blinds( None, mapper )
        blinds._currentPosition = 20
        blinds.reset_position()

        assert ( blinds._currentPosition == 0 )