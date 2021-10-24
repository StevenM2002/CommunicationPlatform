import pytest
import json
import requests

from src import config
from src.error import InputError, AccessError

OK = 200


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
    response = requests.post(
        f"{config.url}/channels/create/v2",
        json={"token": clear_and_register, "name": "", "is_public": True},
    )
    assert response.status_code == InputError.code


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
    assert response.status_code == InputError.code


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
    assert response.status_code == AccessError.code


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


@pytest.fixture
def list_data_v2():
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
    return [token0, token1, token2]


def test_no_channels_listv2(list_data_v2):
    # Use requests.post or requests.delete and stuff to give data
    payload = requests.get(
        config.url + "channels/list/v2", params={"token": list_data_v2[0]}
    )
    assert payload.json() == {"channels": []}
    requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[1], "name": "chan1", "is_public": True},
    ).json()
    payload = requests.get(
        config.url + "channels/list/v2", params={"token": list_data_v2[0]}
    )
    assert payload.json() == {"channels": []}


def test_one_channel_public_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[0], "name": "chan0", "is_public": True},
    ).json()
    payload = requests.get(
        config.url + "channels/list/v2", params={"token": list_data_v2[0]}
    )
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_one_channel_priv_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[0], "name": "chan0", "is_public": False},
    ).json()
    payload = requests.get(
        config.url + "channels/list/v2", params={"token": list_data_v2[0]}
    )
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_two_channels_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[0], "name": "chan0", "is_public": False},
    ).json()
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[0], "name": "chan1", "is_public": True},
    ).json()
    payload = requests.get(
        config.url + "channels/list/v2", params={"token": list_data_v2[0]}
    )
    assert payload.json() == {
        "channels": [
            {"channel_id": chan_id0["channel_id"], "name": "chan0"},
            {"channel_id": chan_id1["channel_id"], "name": "chan1"},
        ]
    }


def test_not_admin_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[0], "name": "chan0", "is_public": True},
    ).json()
    requests.post(
        config.url + "channel/join/v2",
        json={"token": list_data_v2[1], "channel_id": chan_id0["channel_id"]},
    )
    payload = requests.get(
        config.url + "channels/list/v2", params={"token": list_data_v2[0]}
    )
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_multiple_people_in_channel_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[0], "name": "chan0", "is_public": True},
    ).json()
    requests.post(
        config.url + "channel/join/v2",
        json={"token": list_data_v2[1], "channel_id": chan_id0["channel_id"]},
    )
    requests.post(
        config.url + "channel/join/v2",
        json={"token": list_data_v2[2], "channel_id": chan_id0["channel_id"]},
    )
    payload = requests.get(
        config.url + "channels/list/v2", params={"token": list_data_v2[2]}
    )
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_user_not_in_multiple_channels_listv2(list_data_v2):
    requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[0], "name": "chan0", "is_public": False},
    ).json()
    requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[1], "name": "chan1", "is_public": False},
    ).json()
    chan_id2 = requests.post(
        config.url + "channels/create/v2",
        json={"token": list_data_v2[2], "name": "chan2", "is_public": False},
    ).json()
    payload = requests.get(
        config.url + "channels/list/v2", params={"token": list_data_v2[2]}
    )
    assert payload.json() == {
        "channels": [{"channel_id": chan_id2["channel_id"], "name": "chan2"}]
    }


def test_invalid_token_listv2(list_data_v2):
    # requests.post(
    #    config.url + "channels/create/v2", params={list_data_v2[0], "chan0", False}
    # ).json()
    response = requests.get(
        config.url + "channels/list/v2", params={"token": "not.the.token"}
    )
    assert response.status_code == 403


@pytest.fixture
def listall_data_v2():
    requests.delete(config.url + "clear/v1")
    token0 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user0@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]
    token1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user1@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]
    token2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user2@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]

    return [token0, token1, token2]


def test_no_channels_listallv2(listall_data_v2):
    payload = requests.get(
        config.url + "channels/listall/v2", params={"token": listall_data_v2[0]}
    )
    assert payload.json() == {"channels": []}


def test_one_channel_public_listallv2(listall_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": listall_data_v2[0], "name": "chan0", "is_public": True},
    ).json()
    payload = requests.get(
        config.url + "channels/listall/v2", params={"token": listall_data_v2[0]}
    )
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_one_channel_private_listallv2(listall_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": listall_data_v2[0], "name": "chan0", "is_public": False},
    ).json()
    payload = requests.get(
        config.url + "channels/listall/v2", params={"token": listall_data_v2[0]}
    )
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_many_channels_listallv2(listall_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": listall_data_v2[0], "name": "chan0", "is_public": True},
    ).json()
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": listall_data_v2[1], "name": "chan1", "is_public": False},
    ).json()
    chan_id2 = requests.post(
        config.url + "channels/create/v2",
        json={"token": listall_data_v2[2], "name": "chan2", "is_public": True},
    ).json()
    payload = requests.get(
        config.url + "channels/listall/v2", params={"token": listall_data_v2[1]}
    )
    assert payload.json() == {
        "channels": [
            {"channel_id": chan_id0["channel_id"], "name": "chan0"},
            {"channel_id": chan_id1["channel_id"], "name": "chan1"},
            {"channel_id": chan_id2["channel_id"], "name": "chan2"},
        ]
    }


def test_user_is_not_owner_listallv2(listall_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2",
        json={"token": listall_data_v2[0], "name": "chan0", "is_public": True},
    ).json()
    requests.post(
        config.url + "channel/join/v2",
        params={"token": listall_data_v2[1], "channel_id": chan_id0["channel_id"]},
    )
    payload = requests.get(
        config.url + "channels/listall/v2", params={"token": listall_data_v2[1]}
    )
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_invalid_token_listallv2(listall_data_v2):
    # requests.post(
    #    config.url + "channels/create/v2", json={"token": listall_data_v2[0], "name": "chan0", "is_public": True}
    # ).json()
    response = requests.get(
        config.url + "channels/listall/v2", params={"token": "not.valid.token"}
    )
    assert response.status_code == 403
