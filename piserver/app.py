'''
File for basic webserver on the Raspberry Pi to handle API requests.

Attributions:
Code for authentication with JWT's taken from Pretty Printed's YouTube tutorial
at https://www.youtube.com/watch?v=WxGBoY5iNXY and adapted
Original source code from tutorial can be found at: https://s3.us-east-2.amazonaws.com/prettyprinted/jwt_api_example.zip
Multithreading startup based on example from https://networklore.com/start-task-with-flask/

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
from controlalgorithm.angle_step_mapper import AngleStepMapper
from gpiozero import Device
import os
import uuid
from requests import codes as RESP_CODES, get as requests_get
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import time
import threading
import base64

# flask setup
app = Flask(__name__)
appFilePath = os.path.dirname(os.path.abspath(__file__))
cfg = DevelopmentConfig(
) if app.config["ENV"] == "development" else ProductionConfig()
app.config.from_object(cfg)

# set the users db for auth, irrespective of the dev/production config
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + \
    appFilePath + '/users.db'
CORS(app)

db = SQLAlchemy(app)

# INIT BLINDS SYSTEM RELATED COMPONENTS #
temp_sensor = BME280TemperatureSensor() if app.config["USE_TEMP_SENSOR"] \
    else MockTemperatureSensor()

# Init motor driver
STEP_PIN = 20
DIR_PIN = 21
ENABLE_PIN = 25
MS1_PIN = 24
MS2_PIN = 23

# Default User
DEFAULT_USER = "blindUser"

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

'''
Small database model for the users.
Used for authentication with JSON web tokens
'''


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(50))


'''
Decorator for using the JWT token.
Add the @token_required annotation to force that handler to
require a token.
'''


def token_required(fxn):
    @wraps(fxn)
    def decorated(*args, **kwargs):
        token = None

        src_addr = request.remote_addr

        # we skip jwt check for localhost for voice control, but it can be enabled for easier testing
        if (not app.config["JWT_BYPASS_LOCALHOST"] or (app.config["JWT_BYPASS_LOCALHOST"] and src_addr != '127.0.0.1')) and \
                not (app.config["ENV"] == "development" and app.config["JWT_BYPASS_ALL"]):
            if 'x-access-token' in request.headers:
                token = request.headers['x-access-token']

            if not token:
                return make_response("Missing token", RESP_CODES["UNAUTHORIZED"])

            try:
                data = jwt.decode(token, app.config["PISERVER_SECRET_KEY"])
                current_user = User.query.filter_by(
                    public_id=data['public_id']).first()

            except Exception as e:
                return make_response("INVALID TOKEN", RESP_CODES["UNAUTHORIZED"])

        return fxn(*args, **kwargs)

    return decorated


# default empty schedule
app_schedule = BlindsSchedule(BlindMode.DARK, None, None)

mapper = AngleStepMapper()

# Init SmartBlindsSystem object
smart_blinds_system = SmartBlindsSystem(
    Blinds(motor_driver, mapper), app_schedule, temp_sensor)

# END OF INIT BLINDS SYSTEM RELATED COMPONENTS #

# Basic response routes for testing purposes
@app.route('/')
def index():
    return 'Server Works!'


@app.route('/greet')
def say_hello():
    return 'Hello from Server ' + __name__


# Routes for blinds system
'''
API handler to return the current temperature
'''
@app.route(TEMPERATURE_ROUTE, methods=['GET'])
def get_temperature():
    return smart_blinds_system.getTemperature()


'''
API handler to return the current position of the blinds
'''
@app.route(POSITION_ROUTE, methods=['GET', 'POST'] if app.config['ENABLE_POST_POSITION'] else ['GET'])
def handle_position():
    if request.method == 'GET':
        return smart_blinds_system.getPosition()

    # For testing only
    if request.method == 'POST' and app.config['ENABLE_POST_POSITION']:
        return smart_blinds_system.postPosition(request.json)


'''
API handler to handle request to calibrate blind position
'''
@app.route(CALIBRATE_POSITION_ROUTE, methods=['POST'])
def handle_position_calibration():
    return smart_blinds_system.postCalibratePosition()


'''
API hander to return the current status of the system. This includes the position and temperature.
'''
@app.route(STATUS_ROUTE, methods=['GET'])
def get_status():
    return smart_blinds_system.getStatus()


'''
API handler to run the motor test program
'''
@app.route(MOTOR_TEST_ROUTE, methods=['POST'])
def motor_test():
    # run the motor test
    return smart_blinds_system.testMotor()


'''
API handler for endpoints relating to the schedule. This allows for
getting, setting and deleting the currently active schedule.
Requires authenticated user's JWT to use.
'''
@app.route(SCHEDULE_ROUTE, methods=['GET', 'POST', 'DELETE'])
@token_required
def handle_schedule():
    if request.method == 'GET':
        return smart_blinds_system.getSchedule()

    if request.method == 'POST':
        return smart_blinds_system.postSchedule(request.json, forceUpdate=True)

    if request.method == 'DELETE':
        return smart_blinds_system.deleteSchedule(forceUpdate=True)


'''
API handler for setting and clearing manual override commands.
Requires authenticated user's JWT to use.
'''
@app.route(COMMAND_ROUTE, methods=['POST', 'DELETE'])
@token_required
def handle_command():
    if request.method == 'POST':
        command = request.json
        return smart_blinds_system.postBlindsCommand(command, forceUpdate=True)

    if request.method == 'DELETE':
        return smart_blinds_system.deleteBlindsCommand(forceUpdate=True)


### ======== BEGIN AUTH RELATED ROUTES ======== ###
'''
API route handler for listing all users. Mainly serves testing and verification purposes
to allow vieing all current user information.
'''
@app.route(USER_ROUTE, methods=['GET'])
def get_all_users():
    users = User.query.all()

    # build up list to return
    response_data = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password

        response_data.append(user_data)

    return make_response({"users": response_data}, RESP_CODES["OK"])


'''
API route handler for creating a new user.
'''
@app.route(USER_ROUTE, methods=['POST'])
def create_user():
    user_data = request.json
    if user_data is None:
        return make_response("Missing data for user creation", RESP_CODES["BAD_REQUEST"])

    try:
        hashed_password = generate_password_hash(
            user_data['password'], method='sha256')

        new_user = User(public_id=str(uuid.uuid4()),
                        name=user_data['name'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        resp_data = {}
        resp_data["name"] = name = user_data['name']
        resp_data["public_id"] = new_user.public_id

        return make_response(resp_data, RESP_CODES['CREATED'])

    except Exception as err:
        return make_response(str(err), RESP_CODES["BAD_REQUEST"])


'''
Api route handler for deleting an existing user
'''
@app.route(USER_ROUTE, methods=['DELETE'])
def delete_user():
    user_data = request.json

    if user_data is None or "public_id" not in user_data.keys():
        return make_response("Missing data for user deletion", RESP_CODES["BAD_REQUEST"])

    try:
        public_id_to_delete = user_data["public_id"]

        user = User.query.filter_by(public_id=public_id_to_delete).first()

        if not user:
            return make_response("User with id=" + public_id_to_delete + " not found.", RESP_CODES["BAD_REQUEST"])

        db.session.delete(user)
        db.session.commit()

        return make_response({}, RESP_CODES["OK"])

    except Exception as err:
        return make_response(str(err), RESP_CODES["BAD_REQUEST"])


'''
Api route handler for login. Generates are returns a JWT to be used for authentication required requests.
Token duration is controlled by app.config[ "TOKEN_DURATION_MINUTES" ] through the TOKEN_DURATION_MINUTES
environment variable.
'''
@app.route(LOGIN_ROUTE)
def login():
    auth_header = request.headers['authorization']

    if auth_header.split()[0] != "Basic":
        return make_response("Invalid Authorization Type", RESP_CODES["UNAUTHORIZED"], {'WWW-Authenticate': 'Basic realm="Login required!"'})

    auth_arg = auth_header.split()[1]

    # decode from b64
    decoded = base64.standard_b64decode(auth_arg).decode('utf-8').split(":")
    auth_user = decoded[0]
    auth_password = decoded[1]

    # check poorly formed login
    if (not auth_arg or not auth_user or not auth_password):
        return make_response("Could not verify", RESP_CODES["UNAUTHORIZED"], {'WWW-Authenticate': 'Basic realm="Login required!"'})

    # login info is properly formed
    user = User.query.filter_by(name=auth_user).first()

    # no user found for the given username
    if not user:
        return make_response("Could not verify", RESP_CODES["UNAUTHORIZED"], {'WWW-Authenticate': 'Basic realm="Login required!"'})

    # validate password
    if check_password_hash(user.password, auth_password):
        token = jwt.encode({'public_id': user.public_id, 'exp': datetime.datetime.utcnow(
        ) + datetime.timedelta(minutes=app.config["TOKEN_DURATION_MINUTES"])}, app.config['PISERVER_SECRET_KEY'])
        return jsonify({"token": token.decode('UTF-8')}), RESP_CODES['OK']

    # password check failed
    return make_response("Could not verify", RESP_CODES["UNAUTHORIZED"], {'WWW-Authenticate': 'Basic realm="Login required!"'})

### ======== END AUTH RELATED ROUTES ======== ###


'''
Perform setup for running the main loop for the server system.

'''
@app.before_first_request
def start_main_loop():
    smart_blinds_system.activate_main_loop(
        iter_per_min=app.config["SMARTBLINDS_UPDATES_PER_MIN"])


'''
Helper function to force the server to call itself once in order to make the main loop start.

Taken from https://networklore.com/start-task-with-flask/
'''


def start_runner():
    def start_loop():
        not_started = True

        while not_started:
            print('In start loop')
            try:
                r = requests_get('http://127.0.0.1:5000/')
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(2)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()

# if __name__ == "__main__":
#     start_runner()
#     app.run( debug=True )


# Force an api call to itself to ensure that the main loop thread is properly started
start_runner()
