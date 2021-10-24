"""Miscellaneous functions that are used throughout Streams backend.

Contains clear_v1 function and validate_auth_id decorator.
"""


def first(condition, iterable, default=None):
    """Check for first item in iterable matching condition.

    Arguments:
        condition (function) - condition for item to satisfy
        iterable (iterable) - iterable containing items
        default (any) - value to return if no items satisfy condition

    Returns:
        Returns first item matching condition iterable if condition satisfied
        Returns default if condition not satisfied by any items
    """
    return next((item for item in iterable if condition(item)), default)
