"""Miscellaneous functions that are used throughout Streams backend.

Contains clear_v1 function and validate_auth_id decorator.
"""
from copy import deepcopy
from functools import wraps

from src.data_store import data_store, INITIAL_OBJECT
from src.error import AccessError


def clear_v1():
    """Clear the datastore class object to the value of INITIAL_OBJECT."""
    data_store.set(deepcopy(INITIAL_OBJECT))


def validate_auth_id(func):
    """Ensure that the auth_user_id given to a function is valid.

    Arguments:
        func (function) - streams function

    Exceptions:
        AccessError - Occurs when:
            - an auth_user_id is given that doesn't belong to a user
            - from the streams database.

    Returns:
        Returns wrapper function
    """

    @wraps(func)
    def wrapper(auth_user_id, *args, **kwargs):
        for user in data_store.get()["users"]:
            if user["u_id"] == auth_user_id:
                return func(auth_user_id, *args, **kwargs)
        raise AccessError("invalid auth_user_id")

    return wrapper


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
