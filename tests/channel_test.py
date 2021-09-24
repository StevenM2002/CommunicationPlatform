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
    u_id = auth_register_v1("random@gmail.com", "joel", "bryla")
    auth_id = auth_register_v1("example@gmail.com", "lewis", "bandas")
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)
    channel_invite_v1(auth_id, c_id, u_id)
    for each_channel in channels:
        if (each_channel["id"] == c_id):
            the_channel = each_channel
    invite_worked = False
    for each_member in the_channel["all_members"]:
        if (each_member["u_id"] == u_id):
            invite_worked = True
    assert(invite_worked)

def test_invite_invalid_channel():
    clear_v1()
    store = data_store.get()
    u_id = auth_register_v1("random@gmail.com", "joel", "bryla")
    auth_id = auth_register_v1("example@gmail.com", "lewis", "bandas")
    channels = store["channels"]
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, 1, u_id)

def test_invite_invalid_user():
    clear_v1()
    store = data_store.get()
    u_id = auth_register_v1("random@gmail.com", "joel", "bryla")
    auth_id = 15 - u_id
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)

def test_invite_auth_not_member():
    clear_v1()
    store = data_store.get()
    u_id = auth_register_v1("random@gmail.com", "joel", "bryla")
    auth_id = auth_register_v1("example@gmail.com", "lewis", "bandas")
    added_user = auth_register_v1("yeah@gmail.com", "hayden", "smith")
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)
    with pytest.raises(AccessError):
        assert channel_invite_v1(u_id, c_id, added_user)

def test_invite_already_member():
    clear_v1()
    store = data_store.get()
    u_id = auth_register_v1("random@gmail.com", "joel", "bryla")
    auth_id = auth_register_v1("example@gmail.com", "lewis", "bandas")
    channels = store["channels"]
    c_id = channels_create_v1(auth_id, "Test", False)
    channel_invite_v1(auth_id, c_id, u_id)
    with pytest.raises(InputError):
        assert channel_invite_v1(auth_id, c_id, u_id)