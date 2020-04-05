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
    TOKEN_DURATION_MINUTES = int( os.environ.get("TOKEN_DURATION_MINUTES", "30" ) )
    PISERVER_SECRET_KEY = os.environ.get("TOKEN_DURATION_MINUTES", "willekeurigegeheimesleutel" )
    JWT_BYPASS_LOCALHOST = bool(strtobool(os.environ.get("JWT_BYPASS_LOCALHOST", "true").lower()))
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Prevent deprecation warning by explicitly setting false
    ENABLE_POST_POSITION = bool(strtobool(os.environ.get("ENABLE_POST_POSITION", "true").lower()))
    SMARTBLINDS_UPDATES_PER_MIN = float( os.environ.get("SMARTBLINDS_UPDATES_PER_MIN", "1" ) )

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

