from src.data_store import data_store
from src.auth import JWT_SECRET
from src.error import InputError, AccessError
from src.channels import validate_token


def all_users(token):
    """Returns a list of all users when given a valid token

    Arguments:
        token (str) - an encoded JWT token

    Exceptions:
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns users list upon completion

    """
    # Loading the data store
    store = data_store.get()

    # Validating the input token
    u_information = validate_token(token, users)

    # Returning the list of users
    users = [
        {
            "u_id": user["u_id"],
            "email": user["email"],
            "name_first": user["name_first"],
            "name_last": user["name_last"],
            "handle_str": user["handle_str"],
        }
        for user in store["users"]
    ]
    return users


def user_profile(token, u_id):
    """Returns a user's information when given a channel_id

    Arguments:
        token (str) - an encoded JWT token
        u_id (int) - the id of the required user

    Exceptions:
        InputError - Occurs when u_id does not refer to a valid user
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns {name_first, name_last, email, handle_str}

    """
    return user


def user_setname(token, name_first, name_last):
    """Returns a list of all users when given a valid token

    Arguments:
        token (str) - an encoded JWT token
        name_first (str) - user's new first name
        name_last (str) - user's new last name

    Exceptions:
        InputError - Occurs when:
            Length of name_first or name_last is not within 1 to 50 characters
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns {}

    """
    return {}


def user_set_email(token, email):
    """Returns a list of all users when given a valid token

    Arguments:
        token (str) - an encoded JWT token
        email (str) - user's new email

    Exceptions:
        InputError - Occurs when:
            Email is not the valid regular expression
            Email address is already being used by another user
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns {}

    """
    return {}


def user_set_handle(token, handle):
    """Returns a list of all users when given a valid token

    Arguments:
        token (str) - an encoded JWT token
        handle (str)

    Exceptions:
        InputError - Occurs when:
            Length of handle is not within 3 to 20 characters
            handle_str contains non-alphanumeric characters
            The handle is already in use by another user
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns {}

    """
    return {}
