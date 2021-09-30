import pytest

from src.error import InputError, AccessError
from src.other import clear_v1
from src.auth import auth_register_v1
from src.channel import channel_join_v1
from src.channels import channels_list_v1, channels_create_v1


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

    
"""
channels_list_v1
Provide a list of all channels 
(and their associated details) that the authorised user is part of.
"""

@pytest.fixture
def data_set():
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

def test_work_with_stub(data_set):
    chan_id1 = channels_create_v1(data_set[0]["auth_user_id"], "first channel", True)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "first channel"}]
    }


def test_one_channel_public(data_set):
    chan_id1 = channels_create_v1(data_set[0]["auth_user_id"], "one_channel", True)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "one_channel"}]
    }


def test_one_channel_private(data_set):
    chan_id1 = channels_create_v1(data_set[0]["auth_user_id"], "one_channel", False)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "one_channel"}]
    }


def test_two_channels(data_set):
    chan_id1 = channels_create_v1(data_set[0]["auth_user_id"], "first_channel", True)
    chan_id2 = channels_create_v1(data_set[0]["auth_user_id"], "second_channel", False)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "second_channel"},
        ]
    }


def test_not_admin(data_set):
    chan_id1 = channels_create_v1(data_set[0]["auth_user_id"], "first_channel", True)
    channel_join_v1(data_set[1]["auth_user_id"], chan_id1["channel_id"])
    assert channels_list_v1(data_set[1]["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "first_channel"}]
    }


def test_not_in_channels(data_set):
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {"channels": []}
    channels_create_v1(data_set[1]["auth_user_id"], "first_channel", True)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {"channels": []}
    channels_create_v1(data_set[2]["auth_user_id"], "second_channel", False)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {"channels": []}
    channels_create_v1(data_set[1]["auth_user_id"], "third_channel", True)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {"channels": []}


def test_same_channel_name(data_set):
    chan_id1 = channels_create_v1(data_set[0]["auth_user_id"], "first_channel", True)
    chan_id2 = channels_create_v1(data_set[0]["auth_user_id"], "first_channel", False)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "first_channel"},
        ]
    }


def test_mixed_channels(data_set):
    chan_id1 = channels_create_v1(data_set[0]["auth_user_id"], "first_channel", True)
    chan_id2 = channels_create_v1(data_set[0]["auth_user_id"], "second_channel", False)
    chan_id3 = channels_create_v1(data_set[1]["auth_user_id"], "second_channel", True)
    channel_join_v1(data_set[0]["auth_user_id"], chan_id3["channel_id"])
    channels_create_v1(data_set[2]["auth_user_id"], "fourth_channel", False)
    channels_create_v1(data_set[3]["auth_user_id"], "fifth_channel", True)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "second_channel"},
            {"channel_id": chan_id3["channel_id"], "name": "second_channel"},
        ]
    }
