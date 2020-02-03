"""
Date: Jan 31, 2020
Author: Official Python Docs
Modified by: Sam Wu
Contents: Custom exceptions to handle errors
"""

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the inputs for the algorithms.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message