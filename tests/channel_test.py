from src.channels import channels_create_v1
from src.auth import auth_register_v1
import pytest
from src.data_store import data_store
from src.channel import channel_invite_v1
from src.other import clear_v1
from src.error import AccessError, InputError

def test_channel_invite():
    clear_v1()
    store = data_store.get()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", \
        "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    channel_invite_v1(auth_id, c_id, u_id)
    for each_channel in channels:
        if (each_channel["channel_id"] == c_id):
            the_channel = each_channel
    invite_worked = False
    for each_member in the_channel["members"]:
        if (each_member == u_id):
            invite_worked = True
    assert(invite_worked)

def test_invite_invalid_channel():
    clear_v1()
    store = data_store.get()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", \
        "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    channels = store["channels"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, 1, u_id)

def test_invite_invalid_user():
    clear_v1()
    store = data_store.get()
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", \
        "bandas")
    auth_id = auth_dict["auth_user_id"]
    u_id = 15 - auth_id
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)

def test_invite_auth_not_member():
    clear_v1()
    store = data_store.get()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", \
        "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    added_dict = auth_register_v1("yeah@gmail.com", "password", "hayden", \
        "smith")
    added_user = added_dict["auth_user_id"]
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    with pytest.raises(AccessError):
        assert channel_invite_v1(u_id, c_id, added_user)

def test_invite_already_member():
    clear_v1()
    store = data_store.get()
    u_dict = auth_register_v1("random@gmail.com", "password", "joel", "bryla")
    auth_dict = auth_register_v1("example@gmail.com", "password", "lewis", \
        "bandas")
    u_id = u_dict["auth_user_id"]
    auth_id = auth_dict["auth_user_id"]
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)["channel_id"]
    channel_invite_v1(auth_id, c_id, u_id)
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)