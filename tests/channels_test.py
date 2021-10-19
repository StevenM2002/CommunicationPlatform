import pytest

from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v2
from src.channel import channel_join_v1
from src.channels import channels_list_v1, channels_listall_v1, channels_create_v2
from src import config
import json
import requests

OK = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403


@pytest.fixture
def clear_and_register():
    # Clears the data store
    requests.delete(f"{config.url}/clear/v1")
    # Creates a user with id 0
    user = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jon.doe@gmail.com",
            "password": "rabbits",
            "name_first": "Jon",
            "name_last": "Doe",
        },
    )
    user_token = user.json()["token"]
    return user_token


# Channel Create Tests
# Input name is an empty string (input error)
def test_create_empty(clear_and_register):
    print(f"user_token = {clear_and_register}")
    response = requests.post(
        f"{config.url}/channels/create/v2",
        json={"token": clear_and_register, "name": "", "is_public": True},
    )
    print(response.status_code)
    assert response.status_code == INPUT_ERROR


# Input name is greater than 20 characters (input error)
def test_create_large(clear_and_register):
    response = requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": clear_and_register,
            "name": "abcdefghijklmnopqrstuvwxyz",
            "is_public": True,
        },
    )
    assert response.status_code == INPUT_ERROR


# Invalid user_auth_id (access error)
def test_create_inval_auth(clear_and_register):
    response = requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1X2lkIjowLCJzZXNzaW9uX2lkIjoxfQ.RCRXmPo3wjPqok37YkLwhxniIkavLtnNHUJTlWuI",
            "name": "channel",
            "is_public": True,
        },
    )
    assert response.status_code == ACCESS_ERROR


# Valid input name is used with a public chat
def test_create_valid_public(clear_and_register):
    response = requests.post(
        f"{config.url}/channels/create/v2",
        json={"token": clear_and_register, "name": "channel", "is_public": True},
    )
    assert response.status_code == OK
    assert response.json() == {"channel_id": 0}


# Valid input name is used with a private chat
def test_create_valid_private(clear_and_register):
    response = requests.post(
        f"{config.url}/channels/create/v2",
        json={"token": clear_and_register, "name": "channel", "is_public": False},
    )
    assert response.status_code == OK
    assert response.json() == {"channel_id": 0}


# Multiple channels created by the same user with identical channel names,
# making sure different channel IDs are created by the function
def test_create_multiple(clear_and_register):
    first_response = requests.post(
        f"{config.url}/channels/create/v2",
        json={"token": clear_and_register, "name": "channel", "is_public": True},
    )
    second_response = requests.post(
        f"{config.url}/channels/create/v2",
        json={"token": clear_and_register, "name": "second_channel", "is_public": True},
    )
    assert first_response.status_code == OK
    assert first_response.json() == {"channel_id": 0}
    assert second_response.status_code == OK
    assert second_response.json() == {"channel_id": 1}
