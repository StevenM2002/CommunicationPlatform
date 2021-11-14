"""Tests for functions from src/channel.py"""
from src import config
from src.error import InputError, AccessError

import pytest
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
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
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
            "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
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
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            },
            {
                "u_id": 1,
                "email": "jane.citizen@gmail.com",
                "name_first": "Jane",
                "name_last": "Citizen",
                "handle_str": "janecitizen",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
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
            "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
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
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
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
            "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
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
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            },
            {
                "u_id": 1,
                "email": "jane.citizen@gmail.com",
                "name_first": "Jane",
                "name_last": "Citizen",
                "handle_str": "janecitizen",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
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
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            },
            {
                "u_id": 1,
                "email": "jane.citizen@gmail.com",
                "name_first": "Jane",
                "name_last": "Citizen",
                "handle_str": "janecitizen",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
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
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            }
        ],
        "all_members": [
            {
                "u_id": 0,
                "email": "jon.doe@gmail.com",
                "name_first": "Jon",
                "name_last": "Doe",
                "handle_str": "jondoe",
                "profile_img_url": f"{config.url}imgfolder/DEFAULT_IMG.jpg",
            }
        ],
    }


@pytest.fixture
def dataset_addownersv1():
    requests.delete(config.url + "clear/v1")
    reg0 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user1@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    reg1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user2@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    reg2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user3@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()

    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": reg0["token"], "name": "chan0", "is_public": True},
    ).json()["channel_id"]
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": reg1["token"], "name": "chan1", "is_public": True},
    ).json()["channel_id"]

    return {"r": (reg0, reg1, reg2), "c": (chan_id0, chan_id1)}


def test_add_1_owner_addownerv1(dataset_addownersv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_addownersv1["r"][2]["token"],
            "channel_id": dataset_addownersv1["c"][0],
        },
    )
    requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][0]["token"],
            "channel_id": dataset_addownersv1["c"][0],
            "u_id": dataset_addownersv1["r"][2]["auth_user_id"],
        },
    )
    response = requests.get(
        config.url + "channel/details/v2",
        params={
            "token": dataset_addownersv1["r"][2]["token"],
            "channel_id": dataset_addownersv1["c"][0],
        },
    ).json()
    owner_ids = [owners["u_id"] for owners in response["owner_members"]]
    assert dataset_addownersv1["r"][2]["auth_user_id"] in owner_ids


def test_not_in_channel_addowner(dataset_addownersv1):
    response = requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][0]["token"],
            "channel_id": dataset_addownersv1["c"][0],
            "u_id": dataset_addownersv1["r"][2]["auth_user_id"],
        },
    )
    assert response.status_code == 400


def test_invalid_uid_addowner(dataset_addownersv1):
    response = requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][0]["token"],
            "channel_id": dataset_addownersv1["c"][0],
            "u_id": -1,
        },
    )
    assert response.status_code == 400


def test_invalid_token_addowner(dataset_addownersv1):
    response = requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": "not.a.token",
            "channel_id": dataset_addownersv1["c"][0],
            "u_id": dataset_addownersv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 403


def test_invalid_channelid_addowner(dataset_addownersv1):
    response = requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][0]["token"],
            "channel_id": 10,
            "u_id": dataset_addownersv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 400


def test_not_member_of_channel_addowner(dataset_addownersv1):
    response = requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][1]["token"],
            "channel_id": dataset_addownersv1["c"][1],
            "u_id": dataset_addownersv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 400


def test_user_already_owner_addowner(dataset_addownersv1):
    response = requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][1]["token"],
            "channel_id": dataset_addownersv1["c"][1],
            "u_id": dataset_addownersv1["r"][1]["auth_user_id"],
        },
    )
    assert response.status_code == 400


def test_user_does_not_have_owner_perms_addowner(dataset_addownersv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_addownersv1["r"][2]["token"],
            "channel_id": dataset_addownersv1["c"][1],
        },
    )
    response = requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][2]["token"],
            "channel_id": dataset_addownersv1["c"][1],
            "u_id": dataset_addownersv1["r"][2]["auth_user_id"],
        },
    )
    assert response.status_code == 403


def test_add_one_normal_member_addowner(dataset_addownersv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_addownersv1["r"][2]["token"],
            "channel_id": dataset_addownersv1["c"][1],
        },
    )
    requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][1]["token"],
            "channel_id": dataset_addownersv1["c"][1],
            "u_id": dataset_addownersv1["r"][2]["auth_user_id"],
        },
    )
    response = requests.get(
        config.url + "/channel/details/v2",
        params={
            "token": dataset_addownersv1["r"][1]["token"],
            "channel_id": dataset_addownersv1["c"][1],
        },
    ).json()
    owner_ids = [owners["u_id"] for owners in response["owner_members"]]
    assert dataset_addownersv1["r"][2]["auth_user_id"] in owner_ids


def test_add_owner_using_global_owner_to_auth_addowner(dataset_addownersv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_addownersv1["r"][0]["token"],
            "channel_id": dataset_addownersv1["c"][1],
        },
    )
    requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][0]["token"],
            "channel_id": dataset_addownersv1["c"][1],
            "u_id": dataset_addownersv1["r"][0]["auth_user_id"],
        },
    )
    response = requests.get(
        config.url + "/channel/details/v2",
        params={
            "token": dataset_addownersv1["r"][1]["token"],
            "channel_id": dataset_addownersv1["c"][1],
        },
    ).json()
    owner_ids = [owners["u_id"] for owners in response["owner_members"]]
    assert dataset_addownersv1["r"][0]["auth_user_id"] in owner_ids


def test_global_owner_not_a_owner_adding_new_owner(dataset_addownersv1):
    response = requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_addownersv1["r"][0]["token"],
            "channel_id": dataset_addownersv1["c"][1],
            "u_id": dataset_addownersv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 403


@pytest.fixture
def dataset_removeownerv1():
    requests.delete(config.url + "clear/v1")
    reg0 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user0@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    reg1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user1@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    reg2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user2@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": reg0["token"], "name": "chan0", "is_public": True},
    ).json()["channel_id"]
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": reg1["token"], "name": "chan1", "is_public": True},
    ).json()["channel_id"]
    return {"r": (reg0, reg1, reg2), "c": (chan_id0, chan_id1)}


def test_remove_one_owner_removeowner(dataset_removeownerv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_removeownerv1["r"][2]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
        },
    )
    requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][2]["auth_user_id"],
        },
    )
    requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][2]["auth_user_id"],
        },
    )
    response = requests.get(
        config.url + "/channel/details/v2",
        params={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
        },
    ).json()
    owner_ids = [owners["u_id"] for owners in response["owner_members"]]
    assert owner_ids == [dataset_removeownerv1["r"][0]["auth_user_id"]]


def test_remove_self_removeowner(dataset_removeownerv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_removeownerv1["r"][2]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
        },
    )
    requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][2]["auth_user_id"],
        },
    )
    requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][2]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][2]["auth_user_id"],
        },
    )
    response = requests.get(
        config.url + "/channel/details/v2",
        params={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
        },
    ).json()
    owner_ids = [owners["u_id"] for owners in response["owner_members"]]
    assert owner_ids == [dataset_removeownerv1["r"][0]["auth_user_id"]]


def test_remove_with_global_owner_perms(dataset_removeownerv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][1],
        },
    )
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_removeownerv1["r"][2]["token"],
            "channel_id": dataset_removeownerv1["c"][1],
        },
    )
    requests.post(
        config.url + "channel/addowner/v1",
        json={
            "token": dataset_removeownerv1["r"][1]["token"],
            "channel_id": dataset_removeownerv1["c"][1],
            "u_id": dataset_removeownerv1["r"][2]["auth_user_id"],
        },
    )
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][1],
            "u_id": dataset_removeownerv1["r"][1]["auth_user_id"],
        },
    )
    response = requests.get(
        config.url + "/channel/details/v2",
        params={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][1],
        },
    ).json()
    owner_ids = [owners["u_id"] for owners in response["owner_members"]]
    assert owner_ids == [dataset_removeownerv1["r"][2]["auth_user_id"]]


def test_remove_only_owner_removeownerv1(dataset_removeownerv1):
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 400


def test_channel_id_not_valid_removeowner(dataset_removeownerv1):
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": -1,
            "u_id": dataset_removeownerv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 400


def test_userid_not_valid_removeowner(dataset_removeownerv1):
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": -1,
        },
    )
    assert response.status_code == 400


def test_uid_not_a_member_removeowner(dataset_removeownerv1):
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][1]["auth_user_id"],
        },
    )
    assert response.status_code == 400


def test_uid_not_owner_removeowner(dataset_removeownerv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_removeownerv1["r"][1]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
        },
    )
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][0]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][1]["auth_user_id"],
        },
    )
    assert response.status_code == 400


def test_do_not_have_owner_perms_removeowner(dataset_removeownerv1):
    requests.post(
        config.url + "channel/join/v2",
        json={
            "token": dataset_removeownerv1["r"][1]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
        },
    )
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_removeownerv1["r"][1]["token"],
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 403


def test_invalid_token_removeowner(dataset_removeownerv1):
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": "not.valid.token",
            "channel_id": dataset_removeownerv1["c"][0],
            "u_id": dataset_removeownerv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 403


def test_global_owner_not_a_owner_removing_new_owner(dataset_addownersv1):
    response = requests.post(
        config.url + "channel/removeowner/v1",
        json={
            "token": dataset_addownersv1["r"][0]["token"],
            "channel_id": dataset_addownersv1["c"][1],
            "u_id": dataset_addownersv1["r"][0]["auth_user_id"],
        },
    )
    assert response.status_code == 403


@pytest.fixture
def dataset_leavev1():
    requests.delete(config.url + "clear/v1")
    token0 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user1@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]
    token1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user2@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]
    token2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user3@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": token0, "name": "chan0", "is_public": True},
    ).json()["channel_id"]

    return {"t": (token0, token1, token2), "c": (chan_id0, None)}


def test_remove_only_ownermember_leavev1(dataset_leavev1):
    requests.post(
        config.url + "channel/join/v2",
        json={"token": dataset_leavev1["t"][1], "channel_id": dataset_leavev1["c"][0]},
    )
    requests.post(
        config.url + "channel/leave/v1",
        json={"token": dataset_leavev1["t"][0], "channel_id": dataset_leavev1["c"][0]},
    )
    response = requests.get(
        config.url + "channel/details/v2",
        params={
            "token": dataset_leavev1["t"][1],
            "channel_id": dataset_leavev1["c"][0],
        },
    ).json()
    owner_ids = [owners["u_id"] for owners in response["owner_members"]]
    assert owner_ids == []


def test_remove_normal_user_leavev1(dataset_leavev1):
    requests.post(
        config.url + "channel/join/v2",
        json={"token": dataset_leavev1["t"][1], "channel_id": dataset_leavev1["c"][0]},
    )
    requests.post(
        config.url + "channel/leave/v1",
        json={"token": dataset_leavev1["t"][1], "channel_id": dataset_leavev1["c"][0]},
    )
    response = requests.get(
        config.url + "channel/details/v2",
        params={
            "token": dataset_leavev1["t"][0],
            "channel_id": dataset_leavev1["c"][0],
        },
    ).json()
    member_ids = [member["u_id"] for member in response["all_members"]]
    assert member_ids == [0]


def test_channel_id_not_valid_leavev1(dataset_leavev1):
    response = requests.post(
        config.url + "channel/leave/v1",
        json={"token": dataset_leavev1["t"][1], "channel_id": -1},
    )
    assert response.status_code == 400


def test_userid_not_in_channel_leavev1(dataset_leavev1):
    response = requests.post(
        config.url + "channel/leave/v1",
        json={"token": dataset_leavev1["t"][1], "channel_id": dataset_leavev1["c"][0]},
    )
    assert response.status_code == 403


def test_remove_member_many_channels_leavev1(dataset_leavev1):
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": dataset_leavev1["t"][2], "name": "chan1", "is_public": True},
    ).json()["channel_id"]
    requests.post(
        config.url + "channel/join/v2",
        json={"token": dataset_leavev1["t"][0], "channel_id": chan_id1},
    )
    requests.post(
        config.url + "channel/join/v2",
        json={"token": dataset_leavev1["t"][1], "channel_id": chan_id1},
    )
    requests.post(
        config.url + "channel/leave/v1",
        json={"token": dataset_leavev1["t"][0], "channel_id": chan_id1},
    )
    requests.post(
        config.url + "channel/leave/v1",
        json={"token": dataset_leavev1["t"][1], "channel_id": chan_id1},
    )
    response = requests.get(
        config.url + "channel/details/v2",
        params={"token": dataset_leavev1["t"][2], "channel_id": chan_id1},
    ).json()
    member_ids = [member["u_id"] for member in response["all_members"]]
    assert member_ids == [2]


def test_invalid_token_leavev1(dataset_leavev1):
    response = requests.post(
        config.url + "channel/leave/v1",
        json={"token": "not.valid.token", "channel_id": dataset_leavev1["c"][0]},
    )
    assert response.status_code == 403


def test_invalid_chan_id_leavev1(dataset_leavev1):
    response = requests.post(
        config.url + "channel/leave/v1",
        json={"token": dataset_leavev1["t"][0], "channel_id": 10},
    )
    assert response.status_code == 400


def test_member_not_in_channel_leavev1(dataset_leavev1):
    response = requests.post(
        config.url + "channel/leave/v1",
        json={"token": dataset_leavev1["t"][1], "channel_id": dataset_leavev1["c"][0]},
    )
    assert response.status_code == 403


"""Tests for functions from src/channel.py"""


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
        params={"token": user_token, "channel_id": channel_id},
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
        params={"token": token, "channel_id": channel_id},
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
        params={"token": global_token, "channel_id": channel_id},
    )
    assert response.status_code == 200
