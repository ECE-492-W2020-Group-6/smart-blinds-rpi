'''
File for basic webserver on the Raspberry Pi to handle API requests. 

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''

from flask import Flask, request
from flask_cors import CORS
from piserver.api_routes import *
from blinds.blinds_api import Blinds, SmartBlindsSystem
from blinds.blinds_schedule import BlindsSchedule, BlindMode
from piserver.config import DevelopmentConfig, ProductionConfig
from tempsensor.tempsensor import BME280TemperatureSensor, MockTemperatureSensor
from easydriver.easydriver import EasyDriver
from controlalgorithm.angle_step_mapper import AngleStepMapper
from gpiozero import Device

# flask setup
app = Flask(__name__)
cfg = DevelopmentConfig() if app.config["ENV"] == "development" else ProductionConfig()
app.config.from_object(cfg)
CORS(app)

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

#TODO: Init a motor handler here

# default empty schedule 
app_schedule = BlindsSchedule( BlindMode.DARK, None, None )

mapper = AngleStepMapper() 
# Init SmartBlindsSystem object
smart_blinds_system =  SmartBlindsSystem( Blinds( motor_driver, mapper ), app_schedule, temp_sensor )

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

@app.route( POSITION_ROUTE, methods=[ 'GET', 'POST' ] )
def handle_position():
    if request.method == 'GET':
        return smart_blinds_system.getPosition()

    if request.method == 'POST':
        pass 

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

if __name__ == "__main__":
    app.run( debug=True )
