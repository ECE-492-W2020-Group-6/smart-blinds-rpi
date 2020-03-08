"""
Date: Mar 7, 2020
Author: Ishaat Chowdhury
Contents: Contains configuration classes for web server
"""

import os
from distutils.util import strtobool

class Config:
    USE_TEMP_SENSOR = bool(strtobool(os.environ.get("USE_TEMP_SENSOR", "false").lower()))
    USE_MOTOR =  bool(strtobool(os.environ.get("USE_MOTOR", "false").lower()))
    CORS_HEADERS = "Content-Type"

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
