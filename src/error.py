"""Custom errors for Streams.

Contains definitions for AccessError and InputError errors.

    Typical usage example:

    from src.error import AccessError
    raise AccessError("brain too large")
"""


class AccessError(Exception):
    """Access to an operation is not allowed."""


class InputError(Exception):
    """Input to a function is not valid."""
