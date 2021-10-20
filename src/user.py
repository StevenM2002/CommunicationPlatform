from src.data_store import data_store
from src.auth import JWT_SECRET
from src.error import InputError, AccessError
from src.channels import validate_token


def all_users(token):

    return users


def user_profile(token, u_id):

    return user


def user_setname(token, name_first, name_last):

    return {}


def user_set_email(token, email):

    return {}


def user_set_handle(token, handle):

    return {}
