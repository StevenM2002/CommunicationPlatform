import pytest

from src.error import InputError, AccessError
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.other import clear_v1
from src.auth import auth_register_v1
from src.data_store import data_store


@pytest.fixture
def setup_public():
    clear_v1()
    # Creates a user with id 0
    auth_register_v1("jon.doe@gmail.com", "rabbits", "Jon", "Doe")
    # Creates a public channel
    channels_create_v1(0, "public_channel", 1)


@pytest.fixture
def setup_private():
    clear_v1()
    # Creates a user with id 0
    auth_register_v1("jon.doe@gmail.com", "rabbits", "Jon", "Doe")
    # Creates a private channel
    channels_create_v1(0, "private_channel", 0)


# Channel Details Tests
# Input channel_id is invalid
def test_invalid_channel_id(setup_public):
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


"""
def is_in_channel(channels, c_id, u_id):
    for each_channel in channels:
        if each_channel["channel_id"] == c_id:
            the_channel = each_channel
    invite_worked = False
    for each_member in the_channel["members"]:
        if each_member == u_id:
            invite_worked = True
    return invite_worked


# channel invite tests
def test_channel_invite():
    clear_v1()
    store = data_store.get()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    channel_invite_v1(auth_id, c_id, u_id)

    assert is_in_channel(channels, c_id, u_id)


def test_invite_invalid_channel():
    clear_v1()
    store = data_store.get()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, 1, u_id)


def test_invite_invalid_user():
    clear_v1()
    store = data_store.get()
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    auth_id = auth_dict["auth_user_id"]
    u_id = 15 - auth_id
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)


def test_invite_auth_not_member():
    clear_v1()
    store = data_store.get()
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
    store = data_store.get()
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
    store = data_store.get()
    owner_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    auth_id = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")[
        "auth_user_id"
    ]
    c_id = channels_create_v1(owner_id, "Test", True)["channel_id"]
    channel_join_v1(auth_id, c_id)
    assert is_in_channel(store["channels"], c_id, auth_id)


def test_join_invalid_channel():
    clear_v1()
    store = data_store.get()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    with pytest.raises(InputError):
        assert channel_join_v1(auth_id, 1)


def test_join_already_member():
    clear_v1()
    store = data_store.get()
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
    store = data_store.get()
    owner_id = auth_register_v1("random@gmail.com", "password", "joel", "bryla")[
        "auth_user_id"
    ]
    auth_id = auth_register_v1("example@gmail.com", "password", "lewis", "bandas")[
        "auth_user_id"
    ]
    c_id = channels_create_v1(owner_id, "Test", False)["channel_id"]
    with pytest.raises(AccessError):
        assert channel_join_v1(auth_id, c_id)
"""
