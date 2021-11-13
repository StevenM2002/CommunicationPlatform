import math
import time

from src.config import url
from src.error import AccessError, InputError
from src.other import first

import pytest
import requests


@pytest.fixture
def clear_datastore():
    requests.delete(f"{url}clear/v1")


@pytest.fixture
def register_joe(clear_datastore):
    r = requests.post(
        f"{url}auth/register/v2",
        json={
            "name_first": "joe",
            "name_last": "mama",
            "email": "joe@mail.com",
            "password": "password",
        },
    )
    assert r.status_code == 200
    return r.json()["token"], r.json()["auth_user_id"]


@pytest.fixture
def register_bob(clear_datastore):
    r = requests.post(
        f"{url}auth/register/v2",
        json={
            "name_first": "bob",
            "name_last": "mama",
            "email": "bob@mail.com",
            "password": "password",
        },
    )
    assert r.status_code == 200
    return r.json()["token"], r.json()["auth_user_id"]


@pytest.fixture
def register_jeff(clear_datastore):
    r = requests.post(
        f"{url}auth/register/v2",
        json={
            "name_first": "jeff",
            "name_last": "mama",
            "email": "jeff@mail.com",
            "password": "password",
        },
    )
    assert r.status_code == 200
    return r.json()["token"], r.json()["auth_user_id"]


@pytest.fixture
def create_public_channel(register_joe):
    token, user_id = register_joe
    r = requests.post(
        f"{url}channels/create/v2",
        json={"token": token, "name": "test-channel", "is_public": True},
    )
    assert r.status_code == 200
    return user_id, token, r.json()["channel_id"]


@pytest.fixture
def create_private_channel(register_joe):
    token, user_id = register_joe
    r = requests.post(
        f"{url}channels/create/v2",
        json={"token": token, "name": "test-channel", "is_public": False},
    )
    assert r.status_code == 200
    return user_id, token, r.json()["channel_id"]


@pytest.fixture
def create_dm(register_joe, register_bob):
    joe_token, joe_user_id = register_joe
    bob_token, bob_user_id = register_bob
    r = requests.post(
        f"{url}dm/create/v1",
        json={
            "token": joe_token,
            "u_ids": [joe_user_id, bob_user_id],
        },
    )
    assert r.status_code == 200
    dm_id = r.json()["dm_id"]
    return joe_token, joe_user_id, bob_token, bob_user_id, dm_id


def test_message_invalid_token(create_public_channel):
    _, _, channel_id = create_public_channel
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": "", "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == AccessError.code


def test_message_invalid_channel_id(register_joe):
    token, _ = register_joe
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": 0, "start": 0},
    )
    assert r.status_code == InputError.code


def test_message_invalid_start_no_messages(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 1},
    )
    assert r.status_code == InputError.code


def test_message_invalid_start_with_messages(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 1},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 2},
    )
    assert r.status_code == InputError.code


def test_message_user_not_member(create_private_channel, register_bob):
    _, _, channel_id = create_private_channel
    token, _ = register_bob
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == AccessError.code


def test_no_messages(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    messages = r.json()
    assert messages["messages"] == []
    assert messages["start"] == 0
    assert messages["end"] == -1


def test_message_get(create_public_channel):
    user_id, token, channel_id = create_public_channel
    message_text = "hi"
    time_created = math.floor(time.time())
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": message_text},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    messages = r.json()
    assert messages["start"] == 0
    assert messages["end"] == -1
    message = messages["messages"][0]
    assert message["message_id"] == 0
    assert message["u_id"] == user_id
    assert message["message"] == message_text
    assert abs(message["time_created"] - time_created) < 5


def test_message_correct_end(create_public_channel):
    _, token, channel_id = create_public_channel
    start = 5
    end = 55
    for message in range(60):
        r = requests.post(
            f"{url}message/send/v1",
            json={"token": token, "channel_id": channel_id, "message": str(message)},
        )
        assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": start},
    )
    assert r.status_code == 200
    messages = r.json()
    assert messages["start"] == start
    assert messages["end"] == end


def test_message_send_invalid_channel_id(register_joe):
    token, _ = register_joe
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": 0, "message": "message"},
    )
    assert r.status_code == InputError.code


def test_message_send_user_not_member(create_private_channel, register_bob):
    _, _, channel_id = create_private_channel
    token, _ = register_bob
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "message"},
    )
    assert r.status_code == AccessError.code


def test_message_send_message_too_short(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": ""},
    )
    assert r.status_code == InputError.code


def test_message_send_message_too_long(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": " " * 1001},
    )
    assert r.status_code == InputError.code


def test_message_send_joined_user(create_public_channel, register_bob):
    _, _, channel_id = create_public_channel
    bob_token, _ = register_bob
    message_text = "hi"
    r = requests.post(
        f"{url}channel/join/v2", json={"token": bob_token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": bob_token, "channel_id": channel_id, "message": message_text},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": bob_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["message"] == message_text
    assert message["message_id"] == message_id


def test_message_edit_message_too_long(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": token, "message_id": message_id, "message": " " * 1001},
    )
    assert r.status_code == InputError.code


def test_message_edit_message_id_not_valid(create_public_channel):
    _, token, _ = create_public_channel
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": token, "message_id": 0, "message": "hi"},
    )
    assert r.status_code == InputError.code


def test_message_edit_message_not_from_user_and_not_owner(
    create_public_channel, register_bob
):
    _, joe_token, channel_id = create_public_channel
    bob_token, _ = register_bob
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": bob_token, "message_id": message_id, "message": "hi"},
    )
    assert r.status_code == AccessError.code


def test_message_edit_message_not_from_user_and_is_owner(
    create_public_channel, register_bob
):
    _, joe_token, channel_id = create_public_channel
    bob_token, _ = register_bob
    new_message = "hi from the future"
    r = requests.post(
        f"{url}channel/join/v2", json={"token": bob_token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": bob_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": joe_token, "message_id": message_id, "message": new_message},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": joe_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["message"] == new_message
    assert message["message_id"] == message_id


def test_message_edit_message_from_user_and_not_owner(
    create_public_channel, register_bob
):
    _, _, channel_id = create_public_channel
    token, _ = register_bob
    new_message = "hi from the future"
    r = requests.post(
        f"{url}channel/join/v2", json={"token": token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": token, "message_id": message_id, "message": new_message},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["message"] == new_message
    assert message["message_id"] == message_id


def test_message_edit_message_from_user_and_is_owner(create_public_channel):
    _, token, channel_id = create_public_channel
    new_message = "hi from the future"
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": token, "message_id": message_id, "message": new_message},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["message"] == new_message
    assert message["message_id"] == message_id


def test_message_edit_message_from_user_and_is_member(
    create_public_channel, register_bob
):
    _, _, channel_id = create_public_channel
    bob_token, _ = register_bob
    new_message = "hi from the future"
    r = requests.post(
        f"{url}channel/join/v2", json={"token": bob_token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": bob_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": bob_token, "channel_id": channel_id, "message": "there"},
    )
    assert r.status_code == 200
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": bob_token, "message_id": message_id, "message": new_message},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": bob_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = first(lambda m: m["message_id"] == message_id, r.json()["messages"])
    assert message is not None
    assert message["message"] == new_message
    assert message["message_id"] == message_id


def test_message_edit_empty_message(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": token, "message_id": message_id, "message": ""},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert len(messages) == 0


def test_message_edit_dm(create_dm):
    joe_token, _, _, _, dm_id = create_dm
    old_message = "hi"
    new_message = "hi from the future"
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": old_message,
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.put(
        f"{url}message/edit/v1",
        json={
            "token": joe_token,
            "message_id": message_id,
            "message": new_message,
        },
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}dm/messages/v1",
        params={
            "token": joe_token,
            "dm_id": dm_id,
            "start": 0,
        },
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert messages[0]["message"] == new_message


def test_message_send_dm_user_not_member(create_dm, register_jeff):
    _, _, _, _, dm_id = create_dm
    jeff_token, _ = register_jeff
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": jeff_token,
            "message": "hi" * 1000,
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 403


def test_message_send_dm_invalid_dm(create_dm):
    joe_token, _, _, _, _ = create_dm
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": "hi",
            "dm_id": -1,
        },
    )
    assert r.status_code == 400


def test_message_send_dm_message_too_long(create_dm):
    joe_token, _, _, _, dm_id = create_dm
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": "hi" * 1000,
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 400


def test_message_remove_message_id_not_valid(create_public_channel):
    _, token, _ = create_public_channel
    r = requests.delete(
        f"{url}message/remove/v1",
        json={"token": token, "message_id": 0},
    )
    assert r.status_code == InputError.code


def test_message_remove_message_not_from_user_and_not_owner(
    create_public_channel, register_bob
):
    _, joe_token, channel_id = create_public_channel
    bob_token, _ = register_bob
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.delete(
        f"{url}message/remove/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == AccessError.code


def test_message_remove_message_not_from_user_and_is_owner(
    create_public_channel, register_bob
):
    _, joe_token, channel_id = create_public_channel
    bob_token, _ = register_bob
    r = requests.post(
        f"{url}channel/join/v2", json={"token": bob_token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": bob_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.delete(
        f"{url}message/remove/v1",
        json={"token": joe_token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": joe_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert len(messages) == 0


def test_message_remove_message_from_user_and_not_owner(
    create_public_channel, register_bob
):
    _, _, channel_id = create_public_channel
    token, _ = register_bob
    r = requests.post(
        f"{url}channel/join/v2", json={"token": token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.delete(
        f"{url}message/remove/v1", json={"token": token, "message_id": message_id}
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert len(messages) == 0


def test_message_remove_message_from_user_and_is_owner(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.delete(
        f"{url}message/remove/v1", json={"token": token, "message_id": message_id}
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert len(messages) == 0


def test_message_remove_message_from_user_and_is_member(
    create_public_channel, register_bob
):
    _, _, channel_id = create_public_channel
    bob_token, _ = register_bob
    r = requests.post(
        f"{url}channel/join/v2", json={"token": bob_token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": bob_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.delete(
        f"{url}message/remove/v1", json={"token": bob_token, "message_id": message_id}
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": bob_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert len(messages) == 0


def test_message_edit_message_from_removed_user(
    create_public_channel, register_bob, register_jeff
):
    _, joe_token, channel_id = create_public_channel
    bob_token, bob_user_id = register_bob
    jeff_token, _ = register_jeff
    r = requests.post(
        f"{url}channel/join/v2", json={"token": bob_token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": bob_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.delete(
        f"{url}admin/user/remove/v1",
        json={"token": joe_token, "u_id": bob_user_id},
    )
    assert r.status_code == 200
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": jeff_token, "message_id": message_id, "message": "new"},
    )
    assert r.status_code == AccessError.code
    r = requests.put(
        f"{url}message/edit/v1",
        json={"token": joe_token, "message_id": message_id, "message": "new"},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": joe_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    assert r.json()["messages"][0]["message"] == "new"


def test_message_remove_dm(create_dm):
    joe_token, _, _, _, dm_id = create_dm
    message = "hi"
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": message,
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.get(
        f"{url}dm/messages/v1",
        params={
            "token": joe_token,
            "dm_id": dm_id,
            "start": 0,
        },
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert messages[0]["message"] == message
    r = requests.delete(
        f"{url}message/remove/v1",
        json={"token": joe_token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}dm/messages/v1",
        params={
            "token": joe_token,
            "dm_id": dm_id,
            "start": 0,
        },
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert len(messages) == 0


def test_message_remove_dm_from_removed_user(register_jeff, create_dm):
    joe_token, joe_user_id, bob_token, _, dm_id = create_dm
    jeff_token, _ = register_jeff
    message = "hi"
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": message,
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.get(
        f"{url}dm/messages/v1",
        params={
            "token": joe_token,
            "dm_id": dm_id,
            "start": 0,
        },
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert messages[0]["message"] == message
    r = requests.delete(
        f"{url}admin/user/remove/v1",
        json={"token": jeff_token, "u_id": joe_user_id},
    )
    assert r.status_code == 200
    r = requests.delete(
        f"{url}message/remove/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == AccessError.code


def test_message_global_owner_can_edit_memebers_message_channel(
    register_bob, create_public_channel
):
    bob_token, _ = register_bob
    _, joe_token, channel_id = create_public_channel
    message_text = "hi there people"
    new_message_text = "new message"

    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": message_text},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": joe_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["message"] == message_text
    r = requests.put(
        f"{url}message/edit/v1",
        json={
            "token": bob_token,
            "message_id": message_id,
            "message": new_message_text,
        },
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": joe_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["message"] == new_message_text


def test_message_global_owner_cant_edit_memebers_message_dm(register_joe, register_bob):
    joe_token, joe_user_id = register_joe
    bob_token, bob_user_id = register_bob
    r = requests.post(
        f"{url}dm/create/v1",
        json={
            "token": bob_token,
            "u_ids": [joe_user_id, bob_user_id],
        },
    )
    assert r.status_code == 200
    dm_id = r.json()["dm_id"]

    message_text = "hi there people"
    new_message_text = "new message"

    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": bob_token,
            "message": message_text,
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.get(
        f"{url}dm/messages/v1",
        params={
            "token": bob_token,
            "dm_id": dm_id,
            "start": 0,
        },
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert messages[0]["message"] == message_text
    r = requests.put(
        f"{url}message/edit/v1",
        json={
            "token": joe_token,
            "message_id": message_id,
            "message": new_message_text,
        },
    )
    assert r.status_code == AccessError.code
    r = requests.get(
        f"{url}dm/messages/v1",
        params={
            "token": joe_token,
            "dm_id": dm_id,
            "start": 0,
        },
    )
    assert r.status_code == 200
    messages = r.json()["messages"]
    assert messages[0]["message"] == message_text


def test_message_is_not_pinned(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["is_pinned"] == False


def test_message_is_pinned(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["is_pinned"] == True


def test_message_already_pinned(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": token, "message_id": message_id},
    )
    assert r.status_code == InputError.code


def test_message_pin_message_doesnt_exist(create_public_channel):
    _, token, _ = create_public_channel
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": token, "message_id": -1},
    )
    assert r.status_code == InputError.code


def test_message_pin_not_member(create_public_channel, register_bob):
    _, joe_token, channel_id = create_public_channel
    bob_token, _ = register_bob
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == AccessError.code


def test_message_pin_channel_authorised(register_bob, create_public_channel):
    _, joe_token, channel_id = create_public_channel
    bob_token, _ = register_bob
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": joe_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["is_pinned"] == True


def test_message_pin_channel_not_authorised(create_public_channel, register_bob):
    _, _, channel_id = create_public_channel
    token, _ = register_bob
    r = requests.post(
        f"{url}channel/join/v2", json={"token": token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": token, "message_id": message_id},
    )
    assert r.status_code == AccessError.code


def test_message_pin_dm_authorised(create_dm):
    joe_token, _, _, _, dm_id = create_dm
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": "hi",
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": joe_token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}dm/messages/v1",
        params={"token": joe_token, "dm_id": dm_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["is_pinned"] == True


def test_message_pin_dm_not_authorised(create_dm):
    joe_token, _, bob_token, _, dm_id = create_dm
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": "hi",
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == AccessError.code


def test_message_is_unpinned(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["is_pinned"] == True
    r = requests.post(
        f"{url}message/unpin/v1",
        json={"token": token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["is_pinned"] == False


def test_message_already_unpinned(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/unpin/v1",
        json={"token": token, "message_id": message_id},
    )
    assert r.status_code == InputError.code


def test_message_unpin_message_doesnt_exist(create_public_channel):
    _, token, _ = create_public_channel
    r = requests.post(
        f"{url}message/unpin/v1",
        json={"token": token, "message_id": -1},
    )
    assert r.status_code == InputError.code


def test_message_unpin_not_member(create_public_channel, register_bob):
    _, joe_token, channel_id = create_public_channel
    bob_token, _ = register_bob
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/unpin/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == AccessError.code


def test_message_unpin_channel_authorised(register_bob, create_public_channel):
    _, joe_token, channel_id = create_public_channel
    bob_token, _ = register_bob
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/unpin/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": joe_token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["is_pinned"] == False


def test_message_unpin_channel_not_authorised(create_public_channel, register_bob):
    _, _, channel_id = create_public_channel
    token, _ = register_bob
    r = requests.post(
        f"{url}channel/join/v2", json={"token": token, "channel_id": channel_id}
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/unpin/v1",
        json={"token": token, "message_id": message_id},
    )
    assert r.status_code == AccessError.code


def test_message_unpin_dm_authorised(create_dm):
    joe_token, _, _, _, dm_id = create_dm
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": "hi",
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/pin/v1",
        json={"token": joe_token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/unpin/v1",
        json={"token": joe_token, "message_id": message_id},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}dm/messages/v1",
        params={"token": joe_token, "dm_id": dm_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["is_pinned"] == False


def test_message_unpin_dm_not_authorised(create_dm):
    joe_token, _, bob_token, _, dm_id = create_dm
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": "hi",
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/unpin/v1",
        json={"token": bob_token, "message_id": message_id},
    )
    assert r.status_code == AccessError.code


def test_message_react_invalid_message(register_joe):
    token, _ = register_joe
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": token, "message_id": -1, "react_id": 1},
    )
    assert r.status_code == InputError.code


def test_message_react_invalid_react(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": token, "message_id": message_id, "react_id": 0},
    )
    assert r.status_code == InputError.code


def test_message_react_already_exists(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == InputError.code


def test_message_react_not_member_channel(register_bob, create_public_channel):
    bob_token, _ = register_bob
    _, joe_token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": bob_token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == InputError.code


def test_message_react_not_member_dm(register_jeff, create_dm):
    jeff_token, _ = register_jeff
    joe_token, _, _, _, dm_id = create_dm
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": "hi",
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": jeff_token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == InputError.code


def test_message_react_get_react(create_public_channel):
    user_id, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["reacts"] == {str(user_id): [1]}


def test_message_unreact_invalid_message(register_joe):
    token, _ = register_joe
    r = requests.post(
        f"{url}message/unreact/v1",
        json={"token": token, "message_id": -1, "react_id": 1},
    )
    assert r.status_code == InputError.code


def test_message_unreact_invalid_react(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/unreact/v1",
        json={"token": token, "message_id": message_id, "react_id": 0},
    )
    assert r.status_code == InputError.code


def test_message_unreact_doesnt_exists(create_public_channel):
    _, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/unreact/v1",
        json={"token": token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == InputError.code


def test_message_unreact_not_member_channel(register_bob, create_public_channel):
    bob_token, _ = register_bob
    _, joe_token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": joe_token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/unreact/v1",
        json={"token": bob_token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == InputError.code


def test_message_unreact_not_member_dm(register_jeff, create_dm):
    jeff_token, _ = register_jeff
    joe_token, _, _, _, dm_id = create_dm
    r = requests.post(
        f"{url}message/senddm/v1",
        json={
            "token": joe_token,
            "message": "hi",
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/unreact/v1",
        json={"token": jeff_token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == InputError.code


def test_message_unreact_get_react(create_public_channel):
    user_id, token, channel_id = create_public_channel
    r = requests.post(
        f"{url}message/send/v1",
        json={"token": token, "channel_id": channel_id, "message": "hi"},
    )
    assert r.status_code == 200
    message_id = r.json()["message_id"]
    r = requests.post(
        f"{url}message/react/v1",
        json={"token": token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == 200
    r = requests.post(
        f"{url}message/unreact/v1",
        json={"token": token, "message_id": message_id, "react_id": 1},
    )
    assert r.status_code == 200
    r = requests.get(
        f"{url}channel/messages/v2",
        params={"token": token, "channel_id": channel_id, "start": 0},
    )
    assert r.status_code == 200
    message = r.json()["messages"][0]
    assert message["reacts"] == {str(user_id): []}
