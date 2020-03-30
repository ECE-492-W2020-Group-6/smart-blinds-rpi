'''
File for basic webserver on the Raspberry Pi to handle API requests. 

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from piserver.api_routes import *
from blinds.blinds_api import Blinds, SmartBlindsSystem
from blinds.blinds_schedule import BlindsSchedule, BlindMode
from piserver.config import DevelopmentConfig, ProductionConfig
from tempsensor.tempsensor import BME280TemperatureSensor, MockTemperatureSensor
from easydriver.easydriver import EasyDriver
from gpiozero import Device
import os
import uuid
from requests import codes as RESP_CODES
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

# flask setup
app = Flask(__name__)
appFilePath = os.path.dirname( os.path.abspath( __file__ ) )
cfg = DevelopmentConfig() if app.config["ENV"] == "development" else ProductionConfig()
app.config.from_object(cfg)

# set the users db for auth, irrespective of the dev/production config
app.config[ "SQLALCHEMY_DATABASE_URI" ] = 'sqlite:///' + appFilePath + '/users.db'
CORS(app)

db = SQLAlchemy( app )

# INIT BLINDS SYSTEM RELATED COMPONENTS #
temp_sensor = BME280TemperatureSensor() if app.config["USE_TEMP_SENSOR"] \
        else MockTemperatureSensor()

# Init motor driver
STEP_PIN = 20
DIR_PIN = 21
ENABLE_PIN = 25
MS1_PIN = 24
MS2_PIN = 23

# Guard imports behind config flag
# This ensures that server can be run in Docker container
if app.config["USE_MOTOR"]:
    import RPi.GPIO as rpigpio
    from gpiozero.pins.rpigpio import RPiGPIOFactory
    rpigpio.setmode(rpigpio.BCM)
    rpigpio.setwarnings(False)
    Device.pin_factory = RPiGPIOFactory()
else:
    from gpiozero.pins.mock import MockFactory
    Device.pin_factory = MockFactory()

motor_driver = EasyDriver(step_pin=STEP_PIN,
            dir_pin=DIR_PIN, 
            ms1_pin=MS1_PIN, 
            ms2_pin=MS2_PIN,
            enable_pin=ENABLE_PIN)

# setup for auth with jwt
if not "TOKEN_DURATION_MINUTES" in app.config.keys():
    app.config[ "TOKEN_DURATION_MINUTES" ] = 10
else:
    app.config[ "TOKEN_DURATION_MINUTES" ] = int( app.config[ "TOKEN_DURATION_MINUTES" ] )
if not "SECRET_KEY" in app.config.keys():
    app.config[ "SECRET_KEY" ] = "willekeurigegeheimesleutel"
else:
    app.config[ "SECRET_KEY" ] = str( app.config[ "SECRET_KEY" ] )

'''
Small database model for the users.
Used for authentication with JSON web tokens
'''
class User( db.Model ):
    id = db.Column( db.Integer, primary_key=True )
    public_id = db.Column( db.String(50), unique=True )
    name = db.Column( db.String(30), unique=True )
    password = db.Column( db.String(50) )

'''
Decorator for using the JWT token
'''
def token_required( fxn ):
    @wraps(fxn)
    def decorator( *args, **kwargs ):
        token = None

        if 'x-access-token' in request.headers:
            token - request.headers[ 'x-access-token' ]

        if not token:
            return jsonify( {"message": "missing token"} ), RESP_CODES[ "UNAUTHORIZED" ]

        try:
            data = jwt.decode( token, app.config[ "SECRET_KEY" ] )
            current_user = User.query.filter_by( public_id=data[ 'public_id' ] ).first()

        except:
            return jsonify( {"message": "invalid token"} ), RESP_CODES[ "UNAUTHORIZED" ]

        return fxn( *args, **kwargs )

# default empty schedule 
app_schedule = BlindsSchedule( BlindMode.DARK, None, None )

# Init SmartBlindsSystem object
smart_blinds_system =  SmartBlindsSystem( Blinds( motor_driver ), app_schedule, temp_sensor )

# END OF INIT BLINDS SYSTEM RELATED COMPONENTS #

# Basic response routes for testing purposes 
@app.route('/')
def index():
    return 'Server Works!'

@app.route('/greet')
def say_hello():
    return 'Hello from Server'

# Routes for blinds system
@app.route( TEMPERATURE_ROUTE, methods=[ 'GET' ] )
def get_temperature():
    return smart_blinds_system.getTemperature()

@app.route( POSITION_ROUTE, methods=[ 'GET' ] )
def handle_position():
    if request.method == 'GET':
        return smart_blinds_system.getPosition()

@app.route( STATUS_ROUTE, methods=[ 'GET' ] )
def get_status():
    return smart_blinds_system.getStatus()

@app.route( MOTOR_TEST_ROUTE, methods=[ 'POST' ] )
def motor_test():
    # run the motor test
    return smart_blinds_system.testMotor()

@app.route( SCHEDULE_ROUTE, methods=[ 'GET', 'POST', 'DELETE' ])
def handle_schedule():
    if request.method == 'GET':
        return smart_blinds_system.getSchedule()
    
    if request.method == 'POST':
        return smart_blinds_system.postSchedule( request.json )

    if request.method == 'DELETE':
        return smart_blinds_system.deleteSchedule()

@app.route( COMMAND_ROUTE, methods=[ 'POST', 'DELETE' ] )
def handle_command():
    if request.method == 'POST':
        command = request.json
        return smart_blinds_system.postBlindsCommand( command )

    if request.method == 'DELETE':
        return smart_blinds_system.deleteBlindsCommand()


### ======== BEGIN AUTH RELATED ROUTES ======== ###
@app.route( USER_ROUTE, methods=[ 'GET' ] )
def get_all_users():
    users = User.query.all()

    # build up list to return 
    response_data = []
    for user in users:
        user_data = {}
        user_data[ 'public_id' ] = user.public_id
        user_data[ 'name' ] = user.name
        user_data[ 'password' ] = user.password

        response_data.append( user_data )

    return jsonify( { "users":response_data } ), RESP_CODES[ "OK" ]

@app.route( USER_ROUTE, methods=[ 'POST' ] )
def create_user():
    user_data = request.json

    hashed_password = generate_password_hash( user_data[ 'password' ], method='sha256' )
    
    new_user = User( public_id=str( uuid.uuid4() ), name=user_data[ 'name' ], password=hashed_password )
    db.session.add( new_user )
    db.session.commit()

    return jsonify( { "message": "New user created." } ), RESP_CODES[ 'CREATED' ]

@app.route( USER_ROUTE, methods=[ 'DELETE' ] )
def delete_user():
    data = request.json
    public_id_to_delete = data[ "public_id" ]

    user = User.query.filter_by( public_id=public_id_to_delete ).first()

    if not user:
        return jsonify( {"message": "user with id=" + public_id_to_delete + " not found."} ), RESP_CODES[ "BAD_REQUEST" ]

    db.session.delete( user )
    db.session.commit()

    return jsonify( {"message":"user deleted"}), RESP_CODES[ "OK" ]

@app.route( LOGIN_ROUTE )
def login():
    auth = request.authorization

    # check poorly formed login
    if ( not auth or not auth.username or not auth.password ):
        return make_response( "Could not verify", RESP_CODES[ "UNAUTHORIZED" ], {'WWW-Authenticate' : 'Basic realm="Login required!"'} )

    # login info is properly formed
    user = User.query.filter_by( name=auth.username ).first()

    # no user found for the given username
    if not user:
        return make_response( "Could not verify", RESP_CODES[ "UNAUTHORIZED" ], {'WWW-Authenticate' : 'Basic realm="Login required!"'} )

    # validate password 
    if check_password_hash( user.password, auth.password ):
        token = jwt.encode({'public_id' : user.public_id, 'exp' : str( datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config[ "TOKEN_DURATION_MINUTES" ]))}, app.config['SECRET_KEY'] )
        return jsonify( {"token": token.decode( 'UTF-8' ) } )

    # password check failed
    return make_response( "Could not verify", RESP_CODES[ "UNAUTHORIZED" ], {'WWW-Authenticate' : 'Basic realm="Login required!"'} )

### ======== END AUTH RELATED ROUTES ======== ###


if __name__ == "__main__":
    app.run( debug=True )
