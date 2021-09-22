import pytest

from src.error import InputError, AccessError
from src.channels import channels_create_v1
from src.other import clear_v1
# Channel Create Tests
# Input name is an empty string (input error)
def test_create_empty():
    clear_v1()
    with pytest.raises(InputError):
        channels_create_v1('abc', '', 1)

# Input name is greater than 20 characters (input error)
def test_create_large():
    clear_v1()
    with pytest.raises(InputError):
        channels_create_v1('abc', 'abcdefghijklmnopqrstuvwxyz', 1)

# Invalid user_auth_id (access error)
def test_create_inval_auth():
    clear_v1()
    with pytest.raises(AccessError):
        channels_create_v1('abc', 'channel', 1)

# Valid input name is used with a public chat
def test_create_valid_public():
    clear_v1()
    assert(channels_create_v1('abc', 'channel', 1) == 0)

# Valid input name is used with a private chat
def test_create_valid_private():
    clear_v1()
    assert(channels_create_v1('abc', 'channel', 0) == 0)

# Multiple channels created by the same user with identical channel names, 
# making sure different channel IDs are created by the function
def test_create_multiple():
    assert(channels_create_v1('abc', 'channel', 0) == 1)
"""There is no comment on whether we have to verify validity of inputs,
will check with the tutors to ensure that we can assume things like the
boolean value for is_public is correct, same for whether auth_user_id can
be assumed to be correct when input to each function, not just when it is 
created"""