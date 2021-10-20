import pytest

from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v2 as auth_register_v1
from src.channel import channel_join_v1
from src.channels import channels_list_v1, channels_listall_v1, channels_create_v1
import requests
import json
from src import config

"""
@pytest.fixture
def clear_and_register():
    clear_v1()
    # Creates a user with id 0
    auth_register_v1("jon.doe@gmail.com", "rabbits", "Jon", "Doe")


# Channel Create Tests
# Input name is an empty string (input error)
def test_create_empty(clear_and_register):
    with pytest.raises(InputError):
        assert channels_create_v1(0, "", True)


# Input name is greater than 20 characters (input error)
def test_create_large(clear_and_register):
    with pytest.raises(InputError):
        channels_create_v1(0, "abcdefghijklmnopqrstuvwxyz", True)


# Invalid user_auth_id (access error)
def test_create_inval_auth(clear_and_register):
    with pytest.raises(AccessError):
        channels_create_v1("zhyuasf", "channel", True)


# Valid input name is used with a public chat
def test_create_valid_public(clear_and_register):
    assert channels_create_v1(0, "channel", True) == {"channel_id": 0}


# Valid input name is used with a private chat
def test_create_valid_private(clear_and_register):
    assert channels_create_v1(0, "channel", False) == {"channel_id": 0}


# Multiple channels created by the same user with identical channel names,
# making sure different channel IDs are created by the function
def test_create_multiple(clear_and_register):
    assert channels_create_v1(0, "channel", False) == {"channel_id": 0}
    assert channels_create_v1(0, "channel", False) == {"channel_id": 1}


# Following tests are for listall channels func
@pytest.fixture
def data_set_listall():
    clear_v1()
    auth_id0 = auth_register_v1(
        "firstid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id1 = auth_register_v1(
        "secondid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "thirdid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id3 = auth_register_v1(
        "fourthid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id4 = auth_register_v1(
        "fifthid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id5 = auth_register_v1(
        "sixthid@gmail.com", "password", "firstname", "lastname"
    )
    return (
        auth_id0["auth_user_id"],
        auth_id1["auth_user_id"],
        auth_id2["auth_user_id"],
        auth_id3["auth_user_id"],
        auth_id4["auth_user_id"],
        auth_id5["auth_user_id"],
    )


def test_one_channel_public_listall(data_set_listall):
    ch_id = channels_create_v1(data_set_listall[0], "first channel", True)
    assert channels_listall_v1(data_set_listall[0]) == {
        "channels": [{"channel_id": ch_id["channel_id"], "name": "first channel"}]
    }


def test_one_channel_private_listall(data_set_listall):
    ch_id = channels_create_v1(data_set_listall[0], "first channel", False)
    assert channels_listall_v1(data_set_listall[0]) == {
        "channels": [{"channel_id": ch_id["channel_id"], "name": "first channel"}]
    }


def test_two_channels_listall(data_set_listall):
    ch_id1 = channels_create_v1(data_set_listall[0], "first channel", True)
    ch_id2 = channels_create_v1(data_set_listall[1], "second channel", False)
    assert channels_listall_v1(data_set_listall[0]) == {
        "channels": [
            {"channel_id": ch_id1["channel_id"], "name": "first channel"},
            {"channel_id": ch_id2["channel_id"], "name": "second channel"},
        ]
    }


def test_multiple_members_listall(data_set_listall):
    ch_id1 = channels_create_v1(data_set_listall[0], "first channel", True)
    channel_join_v1(data_set_listall[1], ch_id1["channel_id"])
    assert channels_listall_v1(data_set_listall[0]) == {
        "channels": [{"channel_id": ch_id1["channel_id"], "name": "first channel"}]
    }


def test_mixed_listall(data_set_listall):
    ch_id1 = channels_create_v1(data_set_listall[0], "first channel", True)
    ch_id2 = channels_create_v1(data_set_listall[1], "second channel", True)
    ch_id3 = channels_create_v1(data_set_listall[2], "third channel", False)
    channel_join_v1(data_set_listall[3], ch_id2["channel_id"])
    channel_join_v1(data_set_listall[4], ch_id2["channel_id"])
    channel_join_v1(data_set_listall[5], ch_id2["channel_id"])
    assert channels_listall_v1(data_set_listall[0]) == {
        "channels": [
            {"channel_id": ch_id1["channel_id"], "name": "first channel"},
            {"channel_id": ch_id2["channel_id"], "name": "second channel"},
            {"channel_id": ch_id3["channel_id"], "name": "third channel"},
        ]
    }


def test_no_channels_listall(data_set_listall):
    assert channels_listall_v1(data_set_listall[0]) == {"channels": []}


def test_not_auth_user_id_listall():
    clear_v1()
    with pytest.raises(AccessError):
        assert channels_listall_v1(1)


# Following tests are for list channels auth_id is in
@pytest.fixture
def data_set_list():
    clear_v1()
    auth_id0 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    auth_id1 = auth_register_v1(
        "authid2@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "authid3@gmail.com", "password", "firstname", "lastname"
    )
    auth_id3 = auth_register_v1(
        "authid4@gmail.com", "password", "firstname", "lastname"
    )
    return (auth_id0, auth_id1, auth_id2, auth_id3)


def test_work_with_stub_list(data_set_list):
    chan_id1 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "first channel", True
    )
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "first channel"}]
    }


def test_one_channel_public_list(data_set_list):
    chan_id1 = channels_create_v1(data_set_list[0]["auth_user_id"], "one_channel", True)
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "one_channel"}]
    }


def test_one_channel_private_list(data_set_list):
    chan_id1 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "one_channel", False
    )
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "one_channel"}]
    }


def test_two_channels_list(data_set_list):
    chan_id1 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "first_channel", True
    )
    chan_id2 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "second_channel", False
    )
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "second_channel"},
        ]
    }


def test_not_admin_list(data_set_list):
    chan_id1 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "first_channel", True
    )
    channel_join_v1(data_set_list[1]["auth_user_id"], chan_id1["channel_id"])
    assert channels_list_v1(data_set_list[1]["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "first_channel"}]
    }


def test_not_in_channels_list(data_set_list):
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {"channels": []}
    channels_create_v1(data_set_list[1]["auth_user_id"], "first_channel", True)
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {"channels": []}
    channels_create_v1(data_set_list[2]["auth_user_id"], "second_channel", False)
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {"channels": []}
    channels_create_v1(data_set_list[1]["auth_user_id"], "third_channel", True)
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {"channels": []}


def test_same_channel_name_list(data_set_list):
    chan_id1 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "first_channel", True
    )
    chan_id2 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "first_channel", False
    )
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "first_channel"},
        ]
    }


def test_mixed_channels_list(data_set_list):
    chan_id1 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "first_channel", True
    )
    chan_id2 = channels_create_v1(
        data_set_list[0]["auth_user_id"], "second_channel", False
    )
    chan_id3 = channels_create_v1(
        data_set_list[1]["auth_user_id"], "second_channel", True
    )
    channel_join_v1(data_set_list[0]["auth_user_id"], chan_id3["channel_id"])
    channels_create_v1(data_set_list[2]["auth_user_id"], "fourth_channel", False)
    channels_create_v1(data_set_list[3]["auth_user_id"], "fifth_channel", True)
    assert channels_list_v1(data_set_list[0]["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "second_channel"},
            {"channel_id": chan_id3["channel_id"], "name": "second_channel"},
        ]
    }


def test_not_auth_id_list():
    clear_v1()
    with pytest.raises(AccessError):
        assert channels_list_v1(1)
"""


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
    payload = requests.get(config.url + "channels/list/v2", params={"data": list_data_v2[0]})
    print(json.loads(payload.text))
    assert payload.json() == {"channels": []}
    requests.post(config.url + "channels/create/v2", params={list_data_v2[1], "chan1", True})
    payload = requests.get(config.url + "channels/list/v2", params={"data": list_data_v2[0]})
    assert payload.json() == {"channels": []}


def test_one_channel_public_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={list_data_v2[0], "chan0", True}
    )
    payload = requests.get(config.url + "channels/list/v2", params={"data": list_data_v2[0]})
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_one_channel_priv_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={list_data_v2[0], "chan0", False}
    )
    payload = requests.get(config.url + "channels/list/v2", params={"data": list_data_v2[0]})
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }


def test_two_channels_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={list_data_v2[0], "chan0", False}
    )
    chan_id1 = requests.post(
        config.url + "channels/create/v2", params={list_data_v2[0], "chan1", True}
    )
    payload = requests.get(config.url + "channels/list/v2", params={"data": list_data_v2[0]})
    assert payload.json() == {
        "channels": [
            {"channel_id": chan_id0["channel_id"], "name": "chan0"},
            {"channel_id": chan_id1["channel_id"], "name": "chan1"}
        ]
    }
    
def test_not_admin_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={list_data_v2[0], "chan0", False}
    )
    requests.post(
        config.url + "channel/join/v2", params={list_data_v2[1], chan_id0["channel_id"]}
    )    
    payload = requests.get(config.url + "channels/list/v2", params={"data": list_data_v2[0]})
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }

def test_multiple_people_in_channel_listv2(list_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={list_data_v2[0], "chan0", False}
    )
    requests.post(
        config.url + "channel/join/v2", params={list_data_v2[1], chan_id0["channel_id"]}
    )
    requests.post(
        config.url + "channel/join/v2", params={list_data_v2[2], chan_id0["channel_id"]}
    )    
    payload = requests.get(config.url + "channels/list/v2", params={"data": list_data_v2[2]})
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }

def test_user_not_in_multiple_channels_listv2(list_data_v2):
    requests.post(
        config.url + "channels/create/v2", params={list_data_v2[0], "chan0", False}
    )            
    requests.post(
        config.url + "channels/create/v2", params={list_data_v2[1], "chan1", False}
    )   
    chan_id2 = requests.post(
        config.url + "channels/create/v2", params={list_data_v2[2], "chan2", False}
    )   
    payload = requests.get(config.url + "channels/list/v2", params={"data": list_data_v2[2]})    
    assert payload.json() == {
        "channels": [{"channel_id": chan_id2["channel_id"], "name": "chan2"}]
    }

def test_invalid_token_listv2(list_data_v2):
    response = requests.get(config.url + "channels/list/v2", params={"data": "not.the.token"})
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
    payload = requests.get(config.url + "channels/listall/v2", params={"data": listall_data_v2[0]})
    assert payload.json() == {"channels": []}

def test_one_channel_public_listallv2(listall_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={listall_data_v2[0], "chan0", True}
    )
    payload = requests.get(config.url + "channels/listall/v2", params={"data": listall_data_v2[0]})
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }

def test_one_channel_private_listallv2(listall_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={listall_data_v2[0], "chan0", False}
    )
    payload = requests.get(config.url + "channels/listall/v2", params={"data": listall_data_v2[0]})
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }

def test_many_channels_listallv2(listall_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={listall_data_v2[0], "chan0", True}
    )
    chan_id1 = requests.post(
        config.url + "channels/create/v2", params={listall_data_v2[1], "chan1", False}
    )
    chan_id2 = requests.post(
        config.url + "channels/create/v2", params={listall_data_v2[2], "chan2", False}
    )
    payload = requests.get(config.url + "channels/listall/v2", params={"data": listall_data_v2[1]})
    assert payload.json() == {
        "channels": [
            {"channel_id": chan_id0["channel_id"], "name": "chan0"},
            {"channel_id": chan_id1["channel_id"], "name": "chan1"},
            {"channel_id": chan_id2["channel_id"], "name": "chan2"}
        ]
    }

def test_user_is_not_owner_listallv2(listall_data_v2):
    chan_id0 = requests.post(
        config.url + "channels/create/v2", params={listall_data_v2[0], "chan0", True}
    )
    requests.post(
        config.url + "channels/join/v2", params={listall_data_v2[1], chan_id0["channel_id"]}
    )
    payload = requests.get(config.url + "channels/listall/v2", params={"data": listall_data_v2[1]})
    assert payload.json() == {
        "channels": [{"channel_id": chan_id0["channel_id"], "name": "chan0"}]
    }

def test_invalid_token_listallv2(listall_data_v2):
    #requests.post(
    #    config.url + "channels/create/v2", params={listall_data_v2[0], "chan0", True}
    #)
    response = requests.get(config.url + "channels/listall/v2", params={"data": "not.valid.token"})
    assert response.status_code == 403


