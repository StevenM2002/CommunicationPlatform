from src.search import search_v1
from src import config
from src.error import AccessError, InputError
import requests
import pytest
import time
import math


@pytest.fixture
def search_dataset():
    requests.delete(config.url + "clear/v1")
    resp = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user1@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    token0 = resp["token"]
    id0 = resp["auth_user_id"]
    resp = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user2@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    token1 = resp["token"]
    id1 = resp["auth_user_id"]
    resp = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "user3@mail.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    token2 = resp["token"]
    id2 = resp["auth_user_id"]
    return {"t": (token0, token1, token2), "id": (id0, id1, id2)}


def test_no_messages_search(search_dataset):
    response = requests.get(
        config.url + "search/v1",
        params={
            "token": search_dataset["t"][0],
            "query_str": "aaaa",
        },
    )
    assert response.json() == {"messages": []}


def test_input_err_search(search_dataset):
    response = requests.get(
        config.url + "search/v1",
        params={
            "token": search_dataset["t"][0],
            "query_str": "",
        },
    )
    assert response.status_code == InputError.code


def test_match_one_channels_message_search(search_dataset):
    # {message_id, u_id, message, time_created, reacts, is_pinned}
    chan_id0 = requests.post(
        config.url + "/channels/create/v2",
        json={
            "token": search_dataset["t"][0],
            "name": "first_chan",
            "is_public": True,
        },
    ).json()["channel_id"]
    time_created = math.floor(time.time())
    msg_id0 = requests.post(
        config.url + "message/send/v1",
        json={
            "token": search_dataset["t"][0],
            "channel_id": chan_id0,
            "message": "string",
        },
    ).json()["message_id"]
    response = requests.get(
        config.url + "search/v1",
        params={
            "token": search_dataset["t"][0],
            "query_str": "string",
        },
    )
    # message_id, u_id, message, time_created, reacts, is_pinned
    msg = response.json()["messages"][0]
    assert msg["message_id"] == msg_id0
    assert msg["u_id"] == search_dataset["id"][0]
    assert msg["message"] == "string"
    assert abs(msg["time_created"] - time_created) < 5


def test_match_two_channels_message_search(search_dataset):
    chan_id0 = requests.post(
        config.url + "/channels/create/v2",
        json={
            "token": search_dataset["t"][0],
            "name": "first_chan",
            "is_public": True,
        },
    ).json()["channel_id"]
    time_created0 = math.floor(time.time())
    msg_id0 = requests.post(
        config.url + "message/send/v1",
        json={
            "token": search_dataset["t"][0],
            "channel_id": chan_id0,
            "message": "string",
        },
    ).json()["message_id"]
    time_created1 = math.floor(time.time())
    msg_id1 = requests.post(
        config.url + "message/send/v1",
        json={
            "token": search_dataset["t"][0],
            "channel_id": chan_id0,
            "message": "secondstring",
        },
    ).json()["message_id"]
    response = requests.get(
        config.url + "search/v1",
        params={
            "token": search_dataset["t"][0],
            "query_str": "string",
        },
    )
    msg = response.json()["messages"]

    assert msg[0]["message_id"] == msg_id1
    assert msg[0]["u_id"] == search_dataset["id"][0]
    assert msg[0]["message"] == "secondstring"
    assert abs(msg[0]["time_created"] - time_created0) < 5

    assert msg[1]["message_id"] == msg_id0
    assert msg[1]["u_id"] == search_dataset["id"][0]
    assert msg[1]["message"] == "string"
    assert abs(msg[1]["time_created"] - time_created0) < 5


def test_messages_no_match(search_dataset):
    chan_id0 = requests.post(
        config.url + "/channels/create/v2",
        json={
            "token": search_dataset["t"][0],
            "name": "first_chan",
            "is_public": True,
        },
    ).json()["channel_id"]
    msg_id0 = requests.post(
        config.url + "message/send/v1",
        json={
            "token": search_dataset["t"][0],
            "channel_id": chan_id0,
            "message": "nomatch",
        },
    ).json()["message_id"]
    response = requests.get(
        config.url + "search/v1",
        params={
            "token": search_dataset["t"][0],
            "query_str": "string",
        },
    )
    assert response.json() == {"messages": []}


def test_match_one_dm(search_dataset):
    dm_id0 = requests.post(
        config.url + "dm/create/v1",
        json={
            "token": search_dataset["t"][0],
            "u_ids": [search_dataset["id"][0]],
        },
    ).json()["dm_id"]
    msg_id0 = requests.post(
        config.url + "message/senddm/v1",
        json={
            "token": search_dataset["t"][0],
            "message": "firststring",
            "dm_id": dm_id0,
        },
    ).json()["message_id"]
    response = requests.get(
        config.url + "search/v1",
        params={
            "token": search_dataset["t"][0],
            "query_str": "string",
        },
    )
    msg = response.json()["messages"][0]
    assert msg["message_id"] == msg_id0
    assert msg["u_id"] == search_dataset["id"][0]
    assert msg["message"] == "firststring"


def test_mixed(search_dataset):
    dm_id0 = requests.post(
        config.url + "dm/create/v1",
        json={
            "token": search_dataset["t"][0],
            "u_ids": [search_dataset["id"][0]],
        },
    ).json()["dm_id"]
    dm_id1 = requests.post(
        config.url + "dm/create/v1",
        json={
            "token": search_dataset["t"][0],
            "u_ids": [search_dataset["id"][1], search_dataset["id"][2]],
        },
    ).json()["dm_id"]
    msg_id0 = requests.post(
        config.url + "message/senddm/v1",
        json={
            "token": search_dataset["t"][0],
            "message": "badstring",
            "dm_id": dm_id0,
        },
    ).json()["message_id"]
    msg_id1 = requests.post(
        config.url + "message/senddm/v1",
        json={
            "token": search_dataset["t"][1],
            "message": "goodstring",
            "dm_id": dm_id1,
        },
    ).json()["message_id"]
    chan_id0 = requests.post(
        config.url + "/channels/create/v2",
        json={
            "token": search_dataset["t"][1],
            "name": "first_chan",
            "is_public": True,
        },
    ).json()["channel_id"]
    msg_id2 = requests.post(
        config.url + "message/send/v1",
        json={
            "token": search_dataset["t"][1],
            "channel_id": chan_id0,
            "message": "goodstring1",
        },
    ).json()["message_id"]
    response = requests.get(
        config.url + "search/v1",
        params={
            "token": search_dataset["t"][1],
            "query_str": "string",
        },
    )
    msg = response.json()["messages"]
    assert msg[0]["message_id"] == msg_id2
    assert msg[0]["u_id"] == search_dataset["id"][1]
    assert msg[0]["message"] == "goodstring1"
    assert msg[1]["message_id"] == msg_id1
    assert msg[1]["u_id"] == search_dataset["id"][1]
    assert msg[1]["message"] == "goodstring"


