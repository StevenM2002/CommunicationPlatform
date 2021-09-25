import pytest

from src.error import InputError, AccessError
from src.channels import channels_create_v1
from src.other import clear_v1
from src.auth import auth_register_v1


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
