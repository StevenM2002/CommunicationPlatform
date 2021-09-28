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

#Should add a pytest fixture here
def test_work_with_stub():
    clear_v1()
    auth_id1 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    chan_id1 = channels_create_v1(auth_id1["auth_user_id"], "first channe;", True)
    assert channels_list_v1(auth_id1["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "first_channel"}]
    }


def test_one_channel_public():
    clear_v1()
    auth_id1 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    chan_id1 = channels_create_v1(auth_id1["auth_user_id"], "one_channel", True)
    assert channels_list_v1(auth_id1["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "one_channel"}]
    }


def test_one_channel_private():
    clear_v1()
    auth_id1 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    chan_id1 = channels_create_v1(auth_id1["auth_user_id"], "one_channel", False)
    assert channels_list_v1(auth_id1["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "one_channel"}]
    }


def test_two_channels():
    clear_v1()
    auth_id1 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "authid2@gmail.com", "password", "firstname", "lastname"
    )
    chan_id1 = channels_create_v1(auth_id1["auth_user_id"], "first_channel", True)
    chan_id2 = channels_create_v1(auth_id2["auth_user_id"], "second_channel", False)
    assert channels_list_v1(auth_id1["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "second_channel"},
        ]
    }


def test_not_admin():
    clear_v1()
    auth_id1 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "authid2@gmail.com", "password", "firstname", "lastname"
    )
    chan_id1 = channels_create_v1(auth_id1["auth_user_id"], "first_channel", True)
    channel_join_v1(auth_id2["auth_user_id"], chan_id["channel_id"])
    assert channels_list_v1(auth_id2["auth_user_id"]) == {
        "channels": [{"channel_id": chan_id1["channel_id"], "name": "first_channel"}]
    }


def test_not_in_channels():
    clear_v1()
    auth_id1 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "authid2@gmail.com", "password", "firstname", "lastname"
    )
    auth_id3 = auth_register_v1(
        "authid3@gmail.com", "password", "firstname", "lastname"
    )
    assert channels_list_v1(auth_id1["auth_user_id"]) == None
    channels_create_v1(auth_id2["auth_user_id"], "first_channel", True)
    assert channels_list_v1(auth_id1["auth_user_id"]) == None
    channels_create_v1(auth_id3["auth_user_id"], "second_channel", False)
    assert channels_list_v1(auth_id1["auth_user_id"]) == None
    channels_create_v1(auth_id2["auth_user_id"], "third_channel", True)
    assert channels_list_v1(auth_id1["auth_user_id"]) == None


def test_same_channel_name():
    clear_v1()
    auth_id1 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    chan_id1 = channels_create_v1(auth_id1["auth_user_id"], "first_channel", True)
    chan_id2 = channels_create_v1(auth_id1["auth_user_id"], "first_channel", False)
    assert channels_list_v1(auth_id1["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "first_channel"},
        ]
    }


def test_mixed_channels():
    clear_v1()
    auth_id1 = auth_register_v1(
        "authid1@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "authid2@gmail.com", "password", "firstname", "lastname"
    )
    auth_id3 = auth_register_v1(
        "authid3@gmail.com", "password", "firstname", "lastname"
    )
    auth_id4 = auth_register_v1(
        "authid4@gmail.com", "password", "firstname", "lastname"
    )
    chan_id1 = channels_create_v1(auth_id1["auth_user_id"], "first_channel", True)
    chan_id2 = channels_create_v1(auth_id1["auth_user_id"], "second_channel", False)
    chan_id3 = channels_create_v1(auth_id2["auth_user_id"], "second_channel", True)
    channel_join_v1(auth_id1["auth_user_id"], chan_id3["channel_id"])
    channels_create_v1(auth_id3["auth_user_id"], "fourth_channel", False)
    channels_create_v1(auth_id4["auth_user_id"], "fifth_channel", True)
    assert channels_list_v1(auth_id1["auth_user_id"]) == {
        "channels": [
            {"channel_id": chan_id1["channel_id"], "name": "first_channel"},
            {"channel_id": chan_id2["channel_id"], "name": "second_channel"},
            {"channel_id": chan_id3["channel_id"], "name": "second_channel"},
        ]
    }
