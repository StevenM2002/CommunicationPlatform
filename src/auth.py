"""Authentication related interfaces.

This contains the functions for registering and logging into a user's account.

    Typical usage example:

    from src.auth import auth_register_v1
    auth_id = auth_register_v1("mark@gmail.com", "password123")
"""
import re
import jwt
import hashlib
import random
import math
import time
from string import printable

from src.data_store import data_store
from src.error import InputError, AccessError

JWT_SECRET = "".join(random.choice(printable) for _ in range(50))

"""jwt structure
{"u_id": int, "session_id": int}
"""


def auth_login_v2(email, password):
    """Returns the auth_user_id of a registered user.

    Arguments:
        email (str) - email of user
        password (str) - password of user

    Exceptions:
        InputError - Occurs when:
            - email entered does not belong to a user
            - password is not correct

    Return Value:
        Returns {auth_user_id} on successful login
    """

    store = data_store.get()
    users = store["users"]

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    for user in users:
        # check for correct email and password pair
        if user["email"] == email and user["password"] == hashed_password:
            # if correct user generate token
            new_session_id = (
                max(user["session_ids"]) + 1 if len(user["session_ids"]) > 0 else 0
            )
            user["session_ids"].append(new_session_id)
            data_store.set(store)

            token_data = {
                "u_id": user["u_id"],
                "session_id": new_session_id,
            }
            token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")

            return {"auth_user_id": user["u_id"], "token": token}

    raise InputError(description="email and or password was incorrect")


def auth_logout_v1(token):
    """Given an active token, invalidates the token to log the user out.

    Arguments:
        token (str) - An encoded JWT token
    """
    # retreive token's data
    token_data = extract_token(token)

    store = data_store.get()
    users = store["users"]
    for user in users:
        # check for matching user_id
        if user["u_id"] == token_data["u_id"]:
            user["session_ids"].remove(token_data["session_id"])
            data_store.set(store)
    return {}


def auth_register_v2(email, password, name_first, name_last):
    """Create a new Streams account for a user.

    Given a user's first and last name, email address, and password and return
    a new auth_user_id. Handle for a user is made by concatenating first and
    last name. If it matches another user's handle add increasing number to the
    end of handle until a new handle is found.

    Arguments:
        email (str) - email of user
        password (str) - password of user
        name_first (str) - first name of user
        name_last (str) - last name of user

    Exceptions:
        InputError - Occurs when:
            - email does not match email regular expression
            - email address is already being used by another user
            - length of password is less than 6 characters
            - length of name_first is not between 1 and 50 characters inclusive
            - length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        Returns { auth_user_id } on successful registration
    """

    # password, email and name validity checks
    if len(password) < 6:
        raise InputError(description="password must be 6 or more characters long")
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(description="first name must be between 1 and 50 characters")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(description="last name must be between 1 and 50 characters")
    if not re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$", email):
        raise InputError(description="invalid email")

    store = data_store.get()
    users = store["users"]
    # check for existing email
    for user in users:
        if user["email"] == email:
            raise InputError(description="email already belongs to a user")

    # make new user id, maximum current id + 1
    store["max_ids"]["user"] += 1
    user_id = store["max_ids"]["user"]
    data_store.set(store)

    # create handle, concatenate, and check for multiples and add number
    handle = f"{name_first.lower()}{name_last.lower()}"
    handle = re.sub(r"\W+", "", handle)
    handle = handle[:20]

    handle = (
        create_handle(handle, len(handle)) if len(handle) > 0 else create_handle("0", 0)
    )

    if len(users) == 0:
        store["global_owners"].append(user_id)

    password = hashlib.sha256(password.encode()).hexdigest()

    # creating a timestamp for the user stats
    time_stamp = math.floor(time.time())

    # add to user list
    users.append(
        {
            "u_id": user_id,
            "email": email,
            "password": password,
            "name_first": name_first,
            "name_last": name_last,
            "handle_str": handle,
            "session_ids": [1],
            "user_stats": {
                "channels_joined": [
                    {"num_channels_joined": 0, "time_stamp": time_stamp}
                ],
                "dms_joined": [{"num_dms_joined": 0, "time_stamp": time_stamp}],
                "messages_sent": [{"num_messages_sent": 0, "time_stamp": time_stamp}],
            },
        }
    )

    data_store.set(store)

    token_data = {"u_id": user_id, "session_id": 1}
    token = jwt.encode(token_data, JWT_SECRET, algorithm="HS256")

    return {"auth_user_id": user_id, "token": token}


def create_handle(handle, base_length):
    """Creates a unique handle for a user.

    Checks if a handle already exists if so adds an increasing number to the
    handle until a new handle is made.

    Arguments:
        handle (str) - handle to be checked
        base_length (int) - length of non-counter part of handle

    Return Value:
        Returns correct handle when no other similar handles found
    """

    users = data_store.get()["users"]

    for user in users:
        if user["handle_str"] == handle:
            counter = handle[base_length:]
            # set count to 0 if doesn't exist else increment counter
            counter = 0 if counter == "" else int(counter) + 1
            # check if new counter also exists
            return create_handle(handle[:base_length] + str(counter), base_length)
    return handle


def extract_token(token):
    """Verifies if the given token is valid

    Arguments:
        token (str) - An encoded JWT token

    Exceptions:
        InputError - Occurs when:
            - invalid jwt token
            - no matching session id for user

    Return Value:
        Returns { u_id, token } on successful registration
    """
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
