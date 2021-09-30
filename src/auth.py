import re

from src.data_store import data_store
from src.error import InputError


def auth_login_v1(email, password):
    """
    Given a registered user's email and password, returns their `auth_user_id` value.

    Arguments:
        email (string) - email of user
        password (string) - password of user

    Exceptions:
        InputError - Occurs when:
            - email entered does not belong to a user
            - password is not correct

    Return Value:
        Returns { auth_user_id } on successful login"""

    store = data_store.get()
    users = store["users"]
    for user in users:
        # check for correct email and password pair
        if user["email"] == email and user["password"] == password:
            return {
                "auth_user_id": user["u_id"],
            }
    raise InputError

    return {
        "auth_user_id": 1,
    }


def auth_register_v1(email, password, name_first, name_last):
    """
    Given a user's first and last name, email address, and password,
    create a new account for them and return a new `auth_user_id`.

    Handle length < 20 charecters
    if identical handles add number 0,1,2,ect. (num excluded from 20 char limit)

    Arguments:
        email (string) - email of user
        password (string) - password of user
        name_first (string) - first name of user
        name_last (string) - last name of user

    Exceptions:
        InputError - Occurs when:
            - email entered is not a valid email (more in section 6.4)
            - email address is already being used by another user
            - length of password is less than 6 characters
            - length of name_first is not between 1 and 50 characters inclusive
            - length of name_last is not between 1 and 50 characters inclusive

    Return Value:
        Returns { auth_user_id } on successful registration"""

    # password, email and name validity checks
    if len(password) < 6:
        raise InputError
    if 1 > len(name_first) or len(name_first) > 50:
        raise InputError
    if 1 > len(name_last) or len(name_last) > 50:
        raise InputError
    if not re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$", email):
        raise InputError

    store = data_store.get()
    users = store["users"]
    # check for existing email
    for user in users:
        if user["email"] == email:
            raise InputError

    # make new user id, maximum current id + 1
    user_id = max(users, key=lambda x: x["u_id"])["u_id"] + 1 if len(users) > 0 else 0

    # create handle, concatenate, and check for multiples and add number
    handle = f"{name_first.lower()}{name_last.lower()}"[:20]
    handle = handle_check(handle, len(handle))

    # add to user list
    users.append(
        {
            "u_id": user_id,
            "email": email,
            "password": password,
            "name_first": name_first,
            "name_last": name_last,
            "handle_str": handle,
        }
    )
    data_store.set(store)

    return {
        "auth_user_id": user_id,
    }


def handle_check(handle, base_length):
    """
    checks if a given handle already exists and if so will add number to end of handle

    Arguments:
        handle (string) - handle to be checked
        base_length (integer) - length of non-counter part of handle

    Return Value:
        Returns correct handle when no other similar handles found"""

    users = data_store.get()["users"]

    for user in users:
        if user["handle_str"] == handle:
            counter = handle[base_length:]
            if counter == "":
                # if no counter start counter
                counter = 0
            else:
                # if counter increment
                counter = int(counter) + 1
            # check if new counter also exists
            return handle_check(handle[:base_length] + str(counter), base_length)
    return handle
