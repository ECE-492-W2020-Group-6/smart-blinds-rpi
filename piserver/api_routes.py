'''
File for blinds API routes. 
Contains constants for API URL routes

Author: Alex (Yin) Chen
Creation Date: February 1, 2020
'''

API_VERSION = 1

# ---------- API Constants ---------- #
'''
These constants define the URL routes that can be used to access the API. 
'''
API_BASE_ROUTE = "/api/v%d" % API_VERSION

MOTOR_TEST_ROUTE = API_BASE_ROUTE + "/motortest"
TEMPERATURE_ROUTE = API_BASE_ROUTE + "/temp"
POSITION_ROUTE = API_BASE_ROUTE + "/pos"
CALIBRATE_POSITION_ROUTE = API_BASE_ROUTE + "/calibratepos"
STATUS_ROUTE = API_BASE_ROUTE + "/status"
SCHEDULE_ROUTE = API_BASE_ROUTE + "/schedule"
COMMAND_ROUTE = API_BASE_ROUTE + "/command"

USER_ROUTE = API_BASE_ROUTE + "/user"
LOGIN_ROUTE = "/login"

# ---------- END OF API Constants ---------- #
