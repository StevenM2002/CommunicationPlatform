import pytest
from src.channels import channels_create_v1
from src.other import clear_v1
from src.channel import channel_join_v1
from src.channels import channels_listall_v1
from src.auth import auth_register_v1

"""
channels_listall_v1(auth_user_id)

return {'channels': [{'channel_id': 1,'name': 'My Channel',}],}

Provide a list of all channels, including private channels, (and their associated details)

"""


def test_work_dummy_data():
    clear_v1()
    assert channels_listall_v1(1) == {
        "channels": [
            {"channel_id": 1, "name": "first_channel"},
            {"channel_id": 2, "name": "second_channel"},
        ]
    }


def test_one_channel_public():
    clear_v1()
    auth_id = auth_register_v1("firstid@gmail.com", "password", "firstname", "lastname")
    ch_id = channels_create_v1(auth_id["auth_user_id"], "first channel", True)
    assert channels_listall_v1(auth_id["auth_user_id"]) == {
        "channels": [{"channel_id": ch_id["channel_id"], "name": "first channel"}]
    }


def test_one_channel_private():
    clear_v1()
    auth_id = auth_register_v1("firstid@gmail.com", "password", "firstname", "lastname")
    ch_id = channels_create_v1(auth_id["auth_user_id"], "first channel", False)
    assert channels_listall_v1(auth_id["auth_user_id"]) == {
        "channels": [{"channel_id": ch_id["channel_id"], "name": "first channel"}]
    }


def test_two_channels():
    clear_v1()
    auth_id1 = auth_register_v1(
        "firstid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "secondid@gmail.com", "password", "firstname", "lastname"
    )
    ch_id1 = channels_create_v1(auth_id1["auth_user_id"], "first channel", True)
    ch_id2 = channels_create_v1(auth_id2["auth_user_id"], "second channel", False)
    assert channels_listall_v1(auth_id1["auth_user_id"]) == {
        "channels": [
            {"channel_id": ch_id1["channel_id"], "name": "first channel"},
            {"channel_id": ch_id2["channel_id"], "name": "second channel"},
        ]
    }


def test_multiple_members():
    clear_v1()
    auth_id1 = auth_register_v1(
        "firstid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "secondid@gmail.com", "password", "firstname", "lastname"
    )
    ch_id1 = channels_create_v1(auth_id1["auth_user_id"], "first channel", True)
    channel_join_v1(auth_id2["channel_id"], ch_id1["channel_id"])
    assert channels_listall_v1(auth_id1["auth_user_id"]) == {
        "channels": [{"channel_id": ch_id1["channel_id"], "name": "first channel"}]
    }


def test_mixed():
    clear_v1()
    auth_id1 = auth_register_v1(
        "firstid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id2 = auth_register_v1(
        "secondid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id3 = auth_register_v1(
        "thirdid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id4 = auth_register_v1(
        "fourthid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id5 = auth_register_v1(
        "fifthid@gmail.com", "password", "firstname", "lastname"
    )
    auth_id6 = auth_register_v1(
        "sixthid@gmail.com", "password", "firstname", "lastname"
    )
    ch_id1 = channels_create_v1(auth_id1["auth_user_id"], "first channel", True)
    ch_id2 = channels_create_v1(auth_id2["auth_user_id"], "second channel", True)
    ch_id3 = channels_create_v1(auth_id3["auth_user_id"], "third channel", False)
    channel_join_v1(auth_id4["auth_user_id"], ch_id2["channel_id"])
    channel_join_v1(auth_id5["auth_user_id"], ch_id2["channel_id"])
    channel_join_v1(auth_id6["auth_user_id"], ch_id2["channel_id"])
    assert channels_listall_v1(auth_id1["auth_user_id"]) == {
        "channels": [
            {"channel_id": ch_id1["channel_id"], "name": "first channel"},
            {"channel_id": ch_id2["channel_id"], "name": "second channel"},
            {"channel_id": ch_id3["channel_id"], "name": "third channel"},
        ]
    }


def test_no_channels():
    clear_v1()
    auth_id1 = auth_register_v1(
        "firstid@gmail.com", "password", "firstname", "lastname"
    )
    assert channels_listall_v1(auth_id1) == None
