"""Miscellaneous functions that are used throughout Streams backend.

Contains clear_v1 function and validate_auth_id decorator.
"""
import jwt

from src.auth import JWT_SECRET
from src.data_store import data_store
from src.error import AccessError


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
    except jwt.DecodeError:
        raise AccessError(description="invalid jwt token") from Exception

    for user in data_store.get()["users"]:
        if user["u_id"] == token_data["u_id"]:
            if token_data["session_id"] in user["session_ids"]:
                return token_data
            else:
                raise AccessError(description="no matching session id for user")
    raise AccessError(description="no matching user id in database")
