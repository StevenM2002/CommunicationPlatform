"""Tests for functions from src/channel.py"""
import pytest
import requests
import json
from src.error import InputError, AccessError
from src.channel import (
    channel_details_v2,
    channel_join_v1,
    channel_invite_v1,
    channel_messages_v1,
)
from src.channels import channels_create_v2
from src.other import clear_v1
from src.auth import auth_register_v2 as auth_register_v1
from src.data_store import data_store
from src import config
import json
import requests

OK = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403


@pytest.fixture
def setup_public_channel():
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
def setup_private_channel():
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
            "name": "private_channel",
            "is_public": False,
        },
    )
    return user_token.json()["token"]


# Channel Details Tests
# Input channel_id is invalid
def test_invalid_channel_id(setup_public_channel):
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public_channel, "channel_id": 10},
    )
    print(response)
    assert response.status_code == INPUT_ERROR


# Input auth_user_id is invalid
def test_invalid_user_id(setup_public_channel):
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": "asdfvbcasweuyfvh", "channel_id": 0},
    )
    assert response.status_code == ACCESS_ERROR


# User is not a member of the channel
def test_not_member(setup_private_channel):
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
        params={"token": new_token.json()["token"], "channel_id": 0},
    )
    assert response.status_code == ACCESS_ERROR


# Both inputs are valid
def test_valid_inputs(setup_public_channel):
    response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public_channel, "channel_id": 0},
    )
    print(response)
    assert response.status_code == OK
    assert response.json() == {
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
def test_valid_multiple(setup_public_channel):
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
        params={"token": setup_public_channel, "channel_id": 0},
    )
    assert response.status_code == OK
    assert response.json() == {
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
def test_valid_private(setup_private_channel):
    requests.post(
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
        params={"token": setup_private_channel, "channel_id": 0},
    )
    assert response.status_code == OK
    assert response.json() == {
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
def test_multiple_channels(setup_public_channel):
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
        json={
            "token": setup_public_channel,
            "name": "second_channel",
            "is_public": True,
        },
    )
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": setup_public_channel,
            "name": "private_channel",
            "is_public": False,
        },
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
        params={"token": setup_public_channel, "channel_id": 0},
    )
    second_response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public_channel, "channel_id": 1},
    )
    third_response = requests.get(
        f"{config.url}/channel/details/v2",
        params={"token": setup_public_channel, "channel_id": 2},
    )
    assert first_response.json() == {
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
    assert second_response.json() == {
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
    assert third_response.json() == {
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


@pytest.fixture
def setup_public():
    requests.delete(config.url + "clear/v1")
    response = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "jon.doe@gmail.com",
            "password": "rabbits",
            "name_first": "Jon",
            "name_last": "Doe",
        },
    )
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "don.joe@gmail.com",
            "password": "babbits",
            "name_first": "Don",
            "name_last": "Joe",
        },
    )
    user_id = r.json()["auth_user_id"]
    user_token = r.json()["token"]
    token = response.json()["token"]
    token_id = response.json()["auth_user_id"]
    # create a public channel
    response = requests.post(
        config.url + "channels/create/v2",
        json={"token": token, "name": "public_channel", "is_public": True},
    )
    channel_id = response.json()["channel_id"]
    return {
        "user_id": user_id,
        "channel_id": channel_id,
        "token_id": token_id,
        "token": token,
        "user_token": user_token,
    }


@pytest.fixture
def setup_private():
    requests.delete(config.url + "clear/v1")
    resp = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "gon.goe@dmail.com",
            "password": "barrits",
            "name_first": "Noj",
            "name_last": "Eod",
        },
    )
    global_token = resp.json()["token"]
    response = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "jon.doe@gmail.com",
            "password": "rabbits",
            "name_first": "Jon",
            "name_last": "Doe",
        },
    )
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "don.joe@gmail.com",
            "password": "babbits",
            "name_first": "Don",
            "name_last": "Joe",
        },
    )
    user_id = r.json()["auth_user_id"]
    user_token = r.json()["token"]
    token = response.json()["token"]
    token_id = response.json()["auth_user_id"]
    # create a private channel
    response = requests.post(
        config.url + "channels/create/v2",
        json={"token": token, "name": "public_channel", "is_public": False},
    )
    channel_id = response.json()["channel_id"]
    return {
        "user_id": user_id,
        "channel_id": channel_id,
        "token_id": token_id,
        "user_token": user_token,
        "token": token,
        "global_token": global_token,
    }


# channel invite tests
def test_channel_invite(setup_public):
    data = setup_public
    u_id = data["user_id"]
    channel_id = data["channel_id"]
    token = data["token"]
    user_token = data["user_token"]
    response = requests.post(
        config.url + "channel/invite/v2",
        json={"token": token, "channel_id": channel_id, "u_id": u_id},
    )
    assert response.status_code == 200
    response = requests.get(
        config.url + "channel/details/v2",
        json={"token": user_token, "channel_id": channel_id},
    )
    assert response.status_code == 200


def test_invite_invalid_channel(setup_public):
    data = setup_public
    u_id = data["user_id"]
    channel_id = data["channel_id"] + 1
    token = data["token"]
    response = requests.post(
        config.url + "channel/invite/v2",
        json={"token": token, "channel_id": channel_id, "u_id": u_id},
    )
    assert response.status_code == InputError.code


def test_invite_invalid_user(setup_public):
    data = setup_public
    u_id = data["user_id"] + data["token_id"] + 1
    channel_id = data["channel_id"]
    token = data["token"]
    response = requests.post(
        config.url + "channel/invite/v2",
        json={"token": token, "channel_id": channel_id, "u_id": u_id},
    )
    assert response.status_code == InputError.code


def test_invite_auth_not_member(setup_public):
    data = setup_public
    u_id = data["user_id"]
    channel_id = data["channel_id"]
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "lbandas@gmail.com",
            "password": "password",
            "name_first": "Lewis",
            "name_last": "Bandas",
        },
    )
    assert r.status_code == 200
    fake_token = r.json()["token"]
    response = requests.post(
        config.url + "channel/invite/v2",
        json={"token": fake_token, "channel_id": channel_id, "u_id": u_id},
    )
    assert response.status_code == AccessError.code


def test_invite_already_member(setup_public):
    data = setup_public
    u_id = data["user_id"]
    channel_id = data["channel_id"]
    token = data["token"]
    requests.post(
        config.url + "channel/invite/v2",
        json={"token": token, "channel_id": channel_id, "u_id": u_id},
    )
    response = requests.post(
        config.url + "channel/invite/v2",
        json={"token": token, "channel_id": channel_id, "u_id": u_id},
    )
    assert response.status_code == InputError.code


# channel join tests
def test_channel_join(setup_public):
    data = setup_public
    token = data["user_token"]
    channel_id = data["channel_id"]
    response = requests.post(
        config.url + "channel/join/v2", json={"token": token, "channel_id": channel_id}
    )
    assert response.status_code == 200
    response = requests.get(
        config.url + "channel/details/v2",
        json={"token": token, "channel_id": channel_id},
    )
    assert response.status_code == 200


def test_join_invalid_channel(setup_public):
    data = setup_public
    token = data["user_token"]
    channel_id = data["channel_id"] + 1
    response = requests.post(
        config.url + "channel/join/v2", json={"token": token, "channel_id": channel_id}
    )
    assert response.status_code == InputError.code


def test_join_already_member(setup_public):
    data = setup_public
    token = data["user_token"]
    channel_id = data["channel_id"]
    response = requests.post(
        config.url + "channel/join/v2", json={"token": token, "channel_id": channel_id}
    )
    response = requests.post(
        config.url + "channel/join/v2", json={"token": token, "channel_id": channel_id}
    )
    assert response.status_code == InputError.code


def test_join_priv_channel(setup_private):
    data = setup_private
    fake_token = data["user_token"]
    channel_id = data["channel_id"]
    response = requests.post(
        config.url + "channel/join/v2",
        json={"token": fake_token, "channel_id": channel_id},
    )
    assert response.status_code == AccessError.code


def test_join_global_owner(setup_private):
    data = setup_private
    global_token = data["global_token"]
    channel_id = data["channel_id"]
    response = requests.post(
        config.url + "channel/join/v2",
        json={"token": global_token, "channel_id": channel_id},
    )
    assert response.status_code == 200
    response = requests.get(
        config.url + "channel/details/v2",
        json={"token": global_token, "channel_id": channel_id},
    )
    assert response.status_code == 200
