"""Miscellaneous functions that are used throughout Streams backend.

Contains clear_v1 function and validate_auth_id decorator.
"""
from functools import wraps

from src.auth import JWT_SECRET
from src.data_store import data_store
from src.error import AccessError

import jwt


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


def extract_token(token):
    try:
        token_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except:
        raise AccessError(description="invalid jwt token") from Exception

    for user in data_store.get()["users"]:
        if user["u_id"] == token_data["u_id"]:
            if token_data["session_id"] in user["session_ids"]:
                return token_data["u_id"], token_data["session_id"]
            else:
                raise AccessError(description="no matching session id for user")
    raise AccessError(description="no matching user id in database")
