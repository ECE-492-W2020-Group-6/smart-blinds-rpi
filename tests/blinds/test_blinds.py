import pytest
from blinds.blinds_api import Blinds, InvalidBlindPositionException

class TestBlinds:

    '''
    Test rotating blinds changes internal position
    '''
    def test_rotate( self ):
        blinds = Blinds( None )
        assert ( blinds._currentPosition == 0 )

        blinds.rotateToPosition( 12 )
        assert ( blinds._currentPosition == 12 )

        blinds.rotateToPosition( 100 )
        assert ( blinds._currentPosition == 100 )

        blinds.rotateToPosition( -54 )
        assert ( blinds._currentPosition == -54 )

        blinds.rotateToPosition( -100 )
        assert ( blinds._currentPosition == -100 )

    def test_invalid_rotation( self ):
        blinds = Blinds( None )
        with pytest.raises( InvalidBlindPositionException ):
            blinds.rotateToPosition( 101 )

        with pytest.raises( InvalidBlindPositionException ):
            blinds.rotateToPosition( 500 )
        
        with pytest.raises( InvalidBlindPositionException ):
            blinds.rotateToPosition( -101 )

        with pytest.raises( InvalidBlindPositionException ):
            blinds.rotateToPosition( -500 )

    def test_reset_position( self ):
        blinds = Blinds( None )
        blinds._currentPosition = 20
        blinds.reset_position()

        assert ( blinds._currentPosition == 0 )