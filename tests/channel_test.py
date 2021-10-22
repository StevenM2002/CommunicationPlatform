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
from src.auth import auth_register_v2 as auth_register_v1
from src.data_store import data_store

"""
@pytest.fixture
def setup_public():
    clear_v1()
    # create a user with
    user_id = auth_register_v1("jon.doe@gmail.com", "rabbits", "Jon", "Doe")[
        "auth_user_id"
    ]
    # create a public channel
    channels_create_v1(user_id, "public_channel", True)


@pytest.fixture
def setup_private():
    clear_v1()
    # creates a user
    user_id = auth_register_v1("jon.doe@gmail.com", "rabbits", "Jon", "Doe")[
        "auth_user_id"
    ]
    # create a private channel
    channels_create_v1(user_id, "private_channel", False)


# Channel Details Tests
# Input channel_id is invalid
def test_invalid_channel_id(setup_public):
    print(data_store.get())
    with pytest.raises(InputError):
        channel_details_v1(0, 10)


# Input auth_user_id is invalid
def test_invalid_user_id(setup_public):
    with pytest.raises(AccessError):
        channel_details_v1(10, 0)


# User is not a member of the channel
def test_not_member(setup_private):
    # Initialises a new member that isn't a member of the new private channel
    auth_register_v1("jane.citizen@gmail.com", "password", "Jane", "Citizen")
    with pytest.raises(AccessError):
        channel_details_v1(1, 0)


# Both inputs are valid
def test_valid_inputs(setup_public):
    assert channel_details_v1(0, 0) == {
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
    auth_register_v1("jane.citizen@gmail.com", "password", "Jane", "Citizen")
    channel_join_v1(1, 0)
    assert channel_details_v1(0, 0) == {
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
    auth_register_v1("jane.citizen@gmail.com", "password", "Jane", "Citizen")
    assert channel_details_v1(0, 0) == {
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
    auth_register_v1("jane.citizen@gmail.com", "password", "Jane", "Citizen")
    channels_create_v1(0, "second_channel", 1)
    channels_create_v1(0, "private_channel", 0)
    channel_join_v1(1, 0)
    channel_join_v1(1, 1)
    assert channel_details_v1(0, 0) == {
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
    assert channel_details_v1(0, 1) == {
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
    assert channel_details_v1(0, 2) == {
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


# channel invite tests
def test_channel_invite():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    channel_invite_v1(auth_id, c_id, u_id)
    # this function below will throw an access error if u_id is not a member
    # of the channel
    channel_details_v1(u_id, c_id)


def test_invite_invalid_channel():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, 1, u_id)


def test_invite_invalid_user():
    clear_v1()
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    auth_id = auth_dict["auth_user_id"]
    u_id = 15 - auth_id
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)


def test_invite_auth_not_member():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    added_dict = auth_register_v1("yeah@gmail.com", "password", "hayden", "smith")
    added_user = added_dict["auth_user_id"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    with pytest.raises(AccessError):
        assert channel_invite_v1(u_id, c_id, added_user)


def test_invite_already_member():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    channel_invite_v1(auth_id, c_id, u_id)
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)


# channel join tests
def test_channel_join():
    clear_v1()
    owner_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    auth_id = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")[
        "auth_user_id"
    ]
    c_id = channels_create_v1(owner_id, "Test", True)["channel_id"]
    channel_join_v1(auth_id, c_id)
    # this function below will throw an access error if u_id is not a member
    # of the channel
    channel_details_v1(auth_id, c_id)


def test_join_invalid_channel():
    clear_v1()
    auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    auth_id = auth_dict["auth_user_id"]
    with pytest.raises(InputError):
        assert channel_join_v1(auth_id, 1)


def test_join_already_member():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    c_id = channels_create_v1(auth_id, "Test", True)["channel_id"]
    channel_join_v1(u_id, c_id)
    with pytest.raises(InputError):
        assert channel_join_v1(u_id, c_id)


def test_join_priv_channel():
    clear_v1()
    owner_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    auth_id = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")[
        "auth_user_id"
    ]
    c_id = channels_create_v1(owner_id, "Test", False)["channel_id"]
    with pytest.raises(AccessError):
        assert channel_join_v1(auth_id, c_id)


def test_message_invalid_auth():
    clear_v1()
    with pytest.raises(AccessError):
        assert channel_messages_v1(-1, 0, 0)


def test_message_no_channels():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    with pytest.raises(InputError):
        assert channel_messages_v1(auth_id, 1, 0)


def test_message_user_not_member():
    clear_v1()
    auth_id1 = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    auth_id2 = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")[
        "auth_user_id"
    ]
    channel_id = channels_create_v1(auth_id2, "test channel", False)["channel_id"]
    with pytest.raises(AccessError):
        assert channel_messages_v1(auth_id1, channel_id, 0)


def test_no_messages():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    channel_id = channels_create_v1(auth_id, "test channel", True)["channel_id"]
    with pytest.raises(InputError):
        assert channel_messages_v1(auth_id, channel_id, 0)


def test_message_id_greater():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    channel_id = channels_create_v1(auth_id, "test channel", True)["channel_id"]
    data = data_store.get()
    messages = data["channels"][channel_id]["messages"]
    messages.append(
        {
            "message_id": 0,
            "u_id": auth_id,
            "message": "Hello world",
            "time_created": 1582426789,
        }
    )
    data_store.set(data)
    with pytest.raises(InputError):
        assert channel_messages_v1(auth_id, channel_id, 1)


def test_one_message():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    channel_id = channels_create_v1(auth_id, "test channel", True)["channel_id"]
    data = data_store.get()
    messages = data["channels"][channel_id]["messages"]
    message = {
        "message_id": 0,
        "u_id": auth_id,
        "message": "Hello world",
        "time_created": 1582426789,
    }
    messages.append(message)
    data_store.set(data)
    assert channel_messages_v1(auth_id, channel_id, 0) == {
        "messages": [message],
        "start": 0,
        "end": -1,
    }


def test_global_owner_permissions():
    clear_v1()

    global_owner = auth_register_v1(
        "email1@email.com", "password2", "firstverylongname", "lastname"
    )["auth_user_id"]
    user_id1 = auth_register_v1(
        "email2@email.com", "password3", "firstverylongname", "lastname"
    )["auth_user_id"]

    channel_public = channels_create_v1(user_id1, "test", True)["channel_id"]
    channel_join_v1(global_owner, channel_public)

    channel_private = channels_create_v1(user_id1, "test1", False)["channel_id"]
    channel_join_v1(global_owner, channel_private)

"""
"""Tests for functions from src/channel.py"""
import pytest

from src.error import InputError, AccessError

"""
@pytest.fixture
def setup_public():
    clear_v1()
    # create a user with
    user_id = auth_register_v1("jon.doe@gmail.com", "rabbits", "Jon", "Doe")[
        "auth_user_id"
    ]
    # create a public channel
    channels_create_v1(user_id, "public_channel", True)


@pytest.fixture
def setup_private():
    clear_v1()
    # creates a user
    user_id = auth_register_v1("jon.doe@gmail.com", "rabbits", "Jon", "Doe")[
        "auth_user_id"
    ]
    # create a private channel
    channels_create_v1(user_id, "private_channel", False)


# Channel Details Tests
# Input channel_id is invalid
def test_invalid_channel_id(setup_public):
    print(data_store.get())
    with pytest.raises(InputError):
        channel_details_v1(0, 10)


# Input auth_user_id is invalid
def test_invalid_user_id(setup_public):
    with pytest.raises(AccessError):
        channel_details_v1(10, 0)


# User is not a member of the channel
def test_not_member(setup_private):
    # Initialises a new member that isn't a member of the new private channel
    auth_register_v1("jane.citizen@gmail.com", "password", "Jane", "Citizen")
    with pytest.raises(AccessError):
        channel_details_v1(1, 0)


# Both inputs are valid
def test_valid_inputs(setup_public):
    assert channel_details_v1(0, 0) == {
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
    auth_register_v1("jane.citizen@gmail.com", "password", "Jane", "Citizen")
    channel_join_v1(1, 0)
    assert channel_details_v1(0, 0) == {
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
    auth_register_v1("jane.citizen@gmail.com", "password", "Jane", "Citizen")
    assert channel_details_v1(0, 0) == {
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
    auth_register_v1("jane.citizen@gmail.com", "password", "Jane", "Citizen")
    channels_create_v1(0, "second_channel", 1)
    channels_create_v1(0, "private_channel", 0)
    channel_join_v1(1, 0)
    channel_join_v1(1, 1)
    assert channel_details_v1(0, 0) == {
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
    assert channel_details_v1(0, 1) == {
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
    assert channel_details_v1(0, 2) == {
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


# channel invite tests
def test_channel_invite():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    channel_invite_v1(auth_id, c_id, u_id)
    # this function below will throw an access error if u_id is not a member
    # of the channel
    channel_details_v1(u_id, c_id)


def test_invite_invalid_channel():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, 1, u_id)


def test_invite_invalid_user():
    clear_v1()
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    auth_id = auth_dict["auth_user_id"]
    u_id = 15 - auth_id
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)


def test_invite_auth_not_member():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    added_dict = auth_register_v1("yeah@gmail.com", "password", "hayden", "smith")
    added_user = added_dict["auth_user_id"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    with pytest.raises(AccessError):
        assert channel_invite_v1(u_id, c_id, added_user)


def test_invite_already_member():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    channel_invite_v1(auth_id, c_id, u_id)
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)


# channel join tests
def test_channel_join():
    clear_v1()
    owner_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    auth_id = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")[
        "auth_user_id"
    ]
    c_id = channels_create_v1(owner_id, "Test", True)["channel_id"]
    channel_join_v1(auth_id, c_id)
    # this function below will throw an access error if u_id is not a member
    # of the channel
    channel_details_v1(auth_id, c_id)


def test_join_invalid_channel():
    clear_v1()
    auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    auth_id = auth_dict["auth_user_id"]
    with pytest.raises(InputError):
        assert channel_join_v1(auth_id, 1)


def test_join_already_member():
    clear_v1()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    c_id = channels_create_v1(auth_id, "Test", True)["channel_id"]
    channel_join_v1(u_id, c_id)
    with pytest.raises(InputError):
        assert channel_join_v1(u_id, c_id)


def test_join_priv_channel():
    clear_v1()
    owner_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    auth_id = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")[
        "auth_user_id"
    ]
    c_id = channels_create_v1(owner_id, "Test", False)["channel_id"]
    with pytest.raises(AccessError):
        assert channel_join_v1(auth_id, c_id)


def test_message_invalid_auth():
    clear_v1()
    with pytest.raises(AccessError):
        assert channel_messages_v1(-1, 0, 0)


def test_message_no_channels():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    with pytest.raises(InputError):
        assert channel_messages_v1(auth_id, 1, 0)


def test_message_user_not_member():
    clear_v1()
    auth_id1 = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    auth_id2 = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")[
        "auth_user_id"
    ]
    channel_id = channels_create_v1(auth_id2, "test channel", False)["channel_id"]
    with pytest.raises(AccessError):
        assert channel_messages_v1(auth_id1, channel_id, 0)


def test_no_messages():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    channel_id = channels_create_v1(auth_id, "test channel", True)["channel_id"]
    with pytest.raises(InputError):
        assert channel_messages_v1(auth_id, channel_id, 0)


def test_message_id_greater():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    channel_id = channels_create_v1(auth_id, "test channel", True)["channel_id"]
    data = data_store.get()
    messages = data["channels"][channel_id]["messages"]
    messages.append(
        {
            "message_id": 0,
            "u_id": auth_id,
            "message": "Hello world",
            "time_created": 1582426789,
        }
    )
    data_store.set(data)
    with pytest.raises(InputError):
        assert channel_messages_v1(auth_id, channel_id, 1)


def test_one_message():
    clear_v1()
    auth_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    channel_id = channels_create_v1(auth_id, "test channel", True)["channel_id"]
    data = data_store.get()
    messages = data["channels"][channel_id]["messages"]
    message = {
        "message_id": 0,
        "u_id": auth_id,
        "message": "Hello world",
        "time_created": 1582426789,
    }
    messages.append(message)
    data_store.set(data)
    assert channel_messages_v1(auth_id, channel_id, 0) == {
        "messages": [message],
        "start": 0,
        "end": -1,
    }


def test_global_owner_permissions():
    clear_v1()

    global_owner = auth_register_v1(
        "email1@email.com", "password2", "firstverylongname", "lastname"
    )["auth_user_id"]
    user_id1 = auth_register_v1(
        "email2@email.com", "password3", "firstverylongname", "lastname"
    )["auth_user_id"]

    channel_public = channels_create_v1(user_id1, "test", True)["channel_id"]
    channel_join_v1(global_owner, channel_public)

    channel_private = channels_create_v1(user_id1, "test1", False)["channel_id"]
    channel_join_v1(global_owner, channel_private)

"""
"""Tests for functions from src/channel.py"""
import pytest
import requests
import json
from src.error import InputError, AccessError
from src.other import clear_v1
from src.data_store import data_store
from src import config 
import requests 

@pytest.fixture
def setup_public():
    requests.delete(config.url + "clear/v1")
    response = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "jon.doe@gmail.com", 
        "password": "rabbits", 
        "name_first": "Jon", 
        "name_last":"Doe"
        }
    )
    r = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "don.joe@gmail.com", 
        "password": "babbits", 
        "name_first": "Don", 
        "name_last":"Joe"
        }
    )
    user_id = r.json()['auth_user_id']
    user_token = r.json()['token']
    token = response.json()['token']
    token_id = response.json()['auth_user_id']
    # create a public channel
    response = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': token, 'name': 'public_channel', 'is_public': True
        }
    )
    channel_id = response.json()['channel_id']
    return {'user_id': user_id, 'channel_id': channel_id, 'token_id': token_id,\
        'token': token, 'user_token': user_token}
@pytest.fixture
def setup_private():
    requests.delete(config.url + "clear/v1")
    resp = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "gon.goe@dmail.com", 
        "password": "barrits", 
        "name_first": "Noj", 
        "name_last":"Eod"
        }
    )
    global_token = resp.json()['token']
    response = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "jon.doe@gmail.com", 
        "password": "rabbits", 
        "name_first": "Jon", 
        "name_last":"Doe"
        }
    )
    r = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "don.joe@gmail.com", 
        "password": "babbits", 
        "name_first": "Don", 
        "name_last":"Joe"
        }
    )
    user_id = r.json()['auth_user_id']
    user_token = r.json()['token']
    token = response.json()['token']
    token_id = response.json()['auth_user_id']
    # create a private channel
    response = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': token, 'name': 'public_channel', 'is_public': False
        }
    )
    channel_id = response.json()['channel_id']
    return {'user_id': user_id, 'channel_id': channel_id, 'token_id': token_id,\
        'user_token': user_token, 'token': token, 'global_token': global_token}
# channel invite tests
def test_channel_invite(setup_public):
    data = setup_public
    u_id = data['user_id']
    channel_id = data['channel_id']
    token = data['token']
    user_token = data['user_token']
    response = requests.post(config.url + 'channel/invite/v2', 
        json = {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == 200
    response = requests.get(config.url + 'channel/details/v2', 
        params= {
            'token': user_token,
            'channel_id': channel_id
        }
  
    )
    assert response.status_code == 200
def test_invite_invalid_channel(setup_public):
    data = setup_public
    u_id = data['user_id']
    channel_id = data['channel_id'] + 1
    token = data['token']
    response = requests.post(config.url + 'channel/invite/v2', 
        json= {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == InputError.code

def test_invite_invalid_user(setup_public):
    data = setup_public
    u_id = data['user_id'] + data['token_id'] + 1
    channel_id = data['channel_id']
    token = data['token']
    response = requests.post(config.url + 'channel/invite/v2', 
        json= {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == InputError.code

def test_invite_auth_not_member(setup_public):
    data = setup_public
    u_id = data['user_id']
    channel_id = data['channel_id']
    r = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "lbandas@gmail.com", 
        "password": "password", 
        "name_first": "Lewis", 
        "name_last":"Bandas"
        }
    )
    assert r.status_code == 200
    fake_token = r.json()['token']
    response = requests.post(config.url + 'channel/invite/v2', 
        json= {
            'token': fake_token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == AccessError.code


def test_invite_already_member(setup_public):
    data = setup_public
    u_id = data['user_id']
    channel_id = data['channel_id']
    token = data['token']
    requests.post(config.url + 'channel/invite/v2', 
        json = {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    response = requests.post(config.url + 'channel/invite/v2', 
        json = {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == InputError.code

# channel join tests
def test_channel_join(setup_public):
    data = setup_public
    token = data['user_token']
    channel_id = data['channel_id']
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == 200
    response = requests.get(config.url + 'channel/details/v2', 
        params= {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == 200

def test_join_invalid_channel(setup_public):
    data = setup_public
    token = data['user_token']
    channel_id = data['channel_id'] + 1
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == InputError.code



def test_join_already_member(setup_public):
    data = setup_public
    token = data['user_token']
    channel_id = data['channel_id']
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == InputError.code

def test_join_priv_channel(setup_private):
    data = setup_private
    fake_token = data['user_token']
    channel_id = data['channel_id']
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': fake_token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == AccessError.code



def test_join_global_owner(setup_private):
    data = setup_private
    global_token = data['global_token']
    channel_id = data['channel_id']
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': global_token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == 200
    response = requests.get(config.url + 'channel/details/v2', 
        params= {
            'token': global_token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == 200
