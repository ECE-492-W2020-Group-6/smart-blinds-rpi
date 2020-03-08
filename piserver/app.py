'''
File for basic webserver on the Raspberry Pi to handle API requests. 

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''


from flask import Flask, request
from piserver.api_routes import *
from blinds.blinds_api import Blinds, SmartBlindsSystem

# flask setup
app = Flask(__name__)
app.config['TESTING'] = True

# INIT BLINDS SYSTEM RELATED COMPONENTS #
smart_blinds_system =  SmartBlindsSystem( Blinds( None ), None, None )

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

@app.route( SCHEDULE_ROUTE, methods=[ 'GET', 'POST', 'DELETE' ])
def handle_schedule():
    if request.method == 'GET':
        return smart_blinds_system.getSchedule()
    
    if request.method == 'POST':
        return smart_blinds_system.postSchedule( request.form )

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