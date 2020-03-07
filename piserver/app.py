'''
File for basic webserver on the Raspberry Pi to handle API requests. 

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''


from flask import Flask, request
from flask_cors import CORS
from piserver.api_routes import *
from blinds.blinds_api import Blinds, SmartBlindsSystem
from piserver.config import DevelopmentConfig, ProductionConfig
from tempsensor.tempsensor import BME280TemperatureSensor, MockTemperatureSensor

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

rpigpio.setmode(rpigpio.BCM)
rpigpio.setwarnings(False)

Device.pin_factory = RPiGPIOFactory()

motor_driver = EasyDriver(step_pin=STEP_PIN,
            dir_pin=DIR_PIN, 
            ms1_pin=MS1_PIN, 
            ms2_pin=MS2_PIN,
            enable_pin=ENABLE_PIN)

# Init SmartBlindsSystem object
smart_blinds_system = SmartBlindsSystem( Blinds( None ), None, temp_sensor, motor_driver )

@app.route('/')
def index():
    return 'Server Works!'
  
@app.route('/greet')
def say_hello():
    return 'Hello from Server'

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
    smart_blinds_system.testMotor()
    return 0    

@app.route( SCHEDULE_ROUTE, methods=[ 'GET', 'POST', 'DELETE' ])
def handle_schedule():
    if request.method == 'GET':
        return smart_blinds_system.getSchedule()
    
    if request.method == 'POST':
        return smart_blinds_system.postSchedule( request.form )

    if request.method == 'DELETE':
        return smart_blinds_system.deleteSchedule()

@app.route( COMMAND_ROUTE, methods=[ 'POST' ] )
def post_command():
    # TODO parse command, likely extract to new function once we are more clear 
    # on the schema
    position = request.form[ 'position' ]
    duration = request.form[ 'time' ]

    return smart_blinds_system.postBlindsCommand( position, duration )

if __name__ == "__main__":
    app.run( debug=True )
