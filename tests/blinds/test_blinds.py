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
from easydriver.easydriver import EasyDriver, MicroStepResolution, StepDirection

class TestBlinds:
    STEP_PIN = 20
    DIR_PIN = 21
    ENABLE_PIN = 25
    MS1_PIN = 24
    MS2_PIN = 23

    """Creates and returns a fresh instance of a driver for tests.

    Also handles cleanup after the yield.
    
    Yields:
        EasyDriver -- fresh instance of driver for each test
    """
    @pytest.fixture()
    def driver(self):
        driver = EasyDriver(step_pin=self.STEP_PIN,
                    dir_pin=self.DIR_PIN, 
                    ms1_pin=self.MS1_PIN, 
                    ms2_pin=self.MS2_PIN,
                    enable_pin=self.ENABLE_PIN)
        yield driver
        driver.close()

    '''
    Test rotateToPosition to check that the internal position is updated. 
    '''
    def test_rotate( self, driver ):
        mapper = AngleStepMapper()
        blinds = Blinds( driver, mapper )
        
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
    def test_invalid_rotation( self, driver ):
        mapper = AngleStepMapper()
        blinds = Blinds( driver, mapper )
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
    def test_reset_position( self, driver ):
        mapper = AngleStepMapper()
        blinds = Blinds( driver, mapper )
        blinds._currentPosition = 20
        blinds.reset_position()

        assert ( blinds._currentPosition == 0 )