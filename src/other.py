from src.error import AccessError
from src.data_store import data_store, INITIAL_OBJECT

from copy import deepcopy
from functools import wraps


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
        Returns wrapper function"""
    @wraps(func)
    def wrapper(auth_user_id, *args, **kwargs):
        for user in data_store.get()["users"]:
            if user["u_id"] == auth_user_id:
                return func(auth_user_id, *args, **kwargs)
        raise AccessError("Invalid auth_user_id")
    return wrapper
