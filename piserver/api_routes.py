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

TEMPERATURE_ROUTE = API_BASE_ROUTE + "/temp"
POSITION_ROUTE = API_BASE_ROUTE + "/pos"
STATUS_ROUTE = API_BASE_ROUTE + "/status"
SCHEDULE_ROUTE = API_BASE_ROUTE + "/schedule"
COMMAND_ROUTE = API_BASE_ROUTE + "/command"

# ---------- END OF API Constants ---------- #