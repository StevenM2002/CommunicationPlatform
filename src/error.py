"""Custom errors for Streams.

Contains definitions for AccessError and InputError errors.

    Typical usage example:

    from src.error import AccessError
    raise AccessError("brain too large")
"""
from werkzeug.exceptions import HTTPException


class AccessError(HTTPException):
    """Access to an operation is not allowed."""

    code = 403
    message = "No message specified"


class InputError(HTTPException):
    """Input to a function is not valid."""

    code = 400
    message = "No message specified"
