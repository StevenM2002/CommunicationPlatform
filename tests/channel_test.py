"""Tests for functions from src/channel.py"""
import pytest

from src.error import InputError, AccessError
from src.channel import (
    channel_details_v2,
    channel_join_v1,
    channel_invite_v1,
    channel_messages_v1,
)
from src.channels import channels_create_v2
from src.other import clear_v1
from src.auth import auth_register_v2
from src.data_store import data_store
from src import config
import json
import requests

OK = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403


@pytest.fixture
def setup_public():
    # Clears the data store
    requests.delete(f"{config.url}/clear/v1")
    # Creates a user with id 0
    user_token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jon.doe@gmail.com",
            "password": "rabbits",
            "name_first": "Jon",
            "name_last": "Doe",
        },
    )
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": user_token.json()["token"],
            "name": "public_channel",
            "is_public": True,
        },
    )
    return user_token.json()["token"]


@pytest.fixture
def setup_private():
    # Clears the data store
    requests.delete(f"{config.url}/clear/v1")
    # Creates a user with id 0
    user_token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jon.doe@gmail.com",
            "password": "rabbits",
            "name_first": "Jon",
            "name_last": "Doe",
        },
    )
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": user_token.json()["token"],
            "name": "public_channel",
            "is_public": False,
        },
    )
    return user_token.json()["token"]


# Channel Details Tests
# Input channel_id is invalid
def test_invalid_channel_id(setup_public):
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public, "channel_id": 10},
    )
    print(response)
    assert response.status_code == INPUT_ERROR


# Input auth_user_id is invalid
def test_invalid_user_id(setup_public):
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": "asdfvbcasweuyfvh", "channel_id": 0},
    )
    assert response.status_code == ACCESS_ERROR


# User is not a member of the channel
def test_not_member(setup_private):
    # Initialises a new member that isn't a member of the new private channel
    new_token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jane.citizen@gmail.com",
            "password": "password",
            "name_first": "Jane",
            "name_last": "Citizen",
        },
    )
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_private, "channel_id": 0},
    )
    assert response.status_code == INPUT_ERROR


# Both inputs are valid
def test_valid_inputs(setup_public):
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public, "channel_id": 0},
    )
    assert response.status_code == OK
    assert response == {
        "name": "public_channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
    }


# Checking access for multiple users
def test_valid_multiple(setup_public):
    new_token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jane.citizen@gmail.com",
            "password": "password",
            "name_first": "Jane",
            "name_last": "Citizen",
        },
    )
    requests.post(
        f"{config.url}/channel/join/v2",
        json={"token": new_token.json()["token"], "channel_id": 0},
    )
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public, "channel_id": 0},
    )
    assert response.status_code == OK
    assert response == {
        "name": "public_channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            },
            {
                "u_id": 1,
                "email": "jane.citizen@gmail.com",
                "name_first": "Jane",
                "name_last": "Citizen",
                "handle_str": "janecitizen",
            },
        ],
    }


# Checking for private channels, only the owner is included
def test_valid_private(setup_private):
    new_token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jane.citizen@gmail.com",
            "password": "password",
            "name_first": "Jane",
            "name_last": "Citizen",
        },
    )
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_private, "channel_id": 0},
    )
    assert response.status_code == OK
    assert response == {
        "name": "private_channel",
        "is_public": False,
        "owner_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
    }


# Check if it works for new channels
def test_multiple_channels(setup_public):
    new_token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jane.citizen@gmail.com",
            "password": "password",
            "name_first": "Jane",
            "name_last": "Citizen",
        },
    )
    requests.post(
        f"{config.url}/channels/create/v2",
        json={"token": setup_public, "name": "second_channel", "is_public": True},
    )
    requests.post(
        f"{config.url}/channels/create/v2",
        json={"token": setup_public, "name": "private_channel", "is_public": False},
    )
    requests.post(
        f"{config.url}/channel/join/v2",
        json={"token": new_token.json()["token"], "channel_id": 0},
    )
    requests.post(
        f"{config.url}/channel/join/v2",
        json={"token": new_token.json()["token"], "channel_id": 1},
    )
    first_response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public, "channel_id": 0},
    )
    second_response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public, "channel_id": 1},
    )
    third_response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public, "channel_id": 2},
    )
    assert first_response == {
        "name": "public_channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            },
            {
                "u_id": 1,
                "email": "jane.citizen@gmail.com",
                "name_first": "Jane",
                "name_last": "Citizen",
                "handle_str": "janecitizen",
            },
        ],
    }
    assert second_response == {
        "name": "second_channel",
        "is_public": True,
        "owner_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            },
            {
                "u_id": 1,
                "email": "jane.citizen@gmail.com",
                "name_first": "Jane",
                "name_last": "Citizen",
                "handle_str": "janecitizen",
            },
        ],
    }
    assert third_response == {
        "name": "private_channel",
        "is_public": False,
        "owner_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
            }
        ],
    }
