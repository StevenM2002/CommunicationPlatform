import pytest
from src.channels import channels_create_v1
from src.other import clear_v1
from src.channel import channel_join_v1
from src.channels import channels_list_v1
from src.auth import auth_register_v1

"""
channels_list_v1
Provide a list of all channels 
(and their associated details) that the authorised user is part of.

Parameters:
{ auth_user_id }
integer

Return:
{ channels }
List of dictionaries, where each dictionary contains types { channel_id, name }
"""
"""
List both private and public channels
"""
"""
In stub says returned is 
{"channels": [{"channel_id": 1, "name": "My Channel",}],}
as a dictionary of a list of dictionary whereas spec says returns channel which
should just be a list of dictionary
"""

# Should add a pytest fixture here
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
    assert channels_list_v1(data_set[0]["auth_user_id"]) == None
    channels_create_v1(data_set[1]["auth_user_id"], "first_channel", True)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == None
    channels_create_v1(data_set[2]["auth_user_id"], "second_channel", False)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == None
    channels_create_v1(data_set[1]["auth_user_id"], "third_channel", True)
    assert channels_list_v1(data_set[0]["auth_user_id"]) == None


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
