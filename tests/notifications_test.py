import pytest
import requests
from src import config


@pytest.fixture
def notifs_dataset():
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
    handle0 = requests.get(
        config.url + "users/all/v1", params={"token": token0}
    ).json()["users"][0]["handle_str"]
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
    handle1 = requests.get(
        config.url + "users/all/v1", params={"token": token1}
    ).json()["users"][1]["handle_str"]
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
    handle2 = requests.get(
        config.url + "users/all/v1", params={"token": token2}
    ).json()["users"][2]["handle_str"]
    return {
        "t": (token0, token1, token2),
        "id": (id0, id1, id2),
        "h": (handle0, handle1, handle2),
    }


def test_no_notifcations(notifs_dataset):
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][0],
        },
    )
    assert response.json() == {"notifications": []}


def test_one_added_to_channel_notif(notifs_dataset):
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": notifs_dataset["t"][1], "name": "chan1", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "u_id": notifs_dataset["id"][2],
        },
    )

    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][2],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1] + " added you to chan1",
            }
        ]
    }


def test_two_added_to_channel_notifs(notifs_dataset):
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": notifs_dataset["t"][1], "name": "chan1", "is_public": True},
    ).json()["channel_id"]
    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "u_id": notifs_dataset["id"][2],
        },
    )
    chan_id2 = requests.post(
        config.url + "channels/create/v2",
        json={"token": notifs_dataset["t"][0], "name": "chan2", "is_public": True},
    ).json()["channel_id"]
    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][0],
            "channel_id": chan_id2,
            "u_id": notifs_dataset["id"][2],
        },
    )
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][2],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": chan_id2,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][0] + " added you to chan2",
            },
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1] + " added you to chan1",
            },
        ]
    }


def test_one_added_to_dms(notifs_dataset):
    dm_id1 = requests.post(
        config.url + "dm/create/v1",
        json={
            "token": notifs_dataset["t"][1],
            "u_ids": [notifs_dataset["id"][2], notifs_dataset["id"][0]],
        },
    ).json()["dm_id"]
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][2],
        },
    )

    assert response.json() == {
        "notifications": [
            {
                "channel_id": -1,
                "dm_id": dm_id1,
                "notification_message": notifs_dataset["h"][1]
                + " added you to firstlast, firstlast0, firstlast1",
            },
        ]
    }


def test_two_added_to_dms(notifs_dataset):
    dm_id1 = requests.post(
        config.url + "dm/create/v1",
        json={
            "token": notifs_dataset["t"][1],
            "u_ids": [notifs_dataset["id"][0], notifs_dataset["id"][2]],
        },
    ).json()["dm_id"]
    dm_id2 = requests.post(
        config.url + "dm/create/v1",
        json={
            "token": notifs_dataset["t"][2],
            "u_ids": [notifs_dataset["id"][0], notifs_dataset["id"][1]],
        },
    ).json()["dm_id"]
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][0],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": -1,
                "dm_id": dm_id2,
                "notification_message": notifs_dataset["h"][2]
                + " added you to firstlast, firstlast0, firstlast1",
            },
            {
                "channel_id": -1,
                "dm_id": dm_id1,
                "notification_message": notifs_dataset["h"][1]
                + " added you to firstlast, firstlast0, firstlast1",
            },
        ]
    }


def test_tagged_once_in_channel(notifs_dataset):
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": notifs_dataset["t"][1], "name": "chan1", "is_public": True},
    ).json()["channel_id"]
    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "u_id": notifs_dataset["id"][2],
        },
    )
    requests.post(
        config.url + "message/send/v1",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "message": "@firstlast1",
        },
    )
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][2],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1]
                + " tagged you in chan1: @firstlast1",
            },
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1] + " added you to chan1",
            },
        ]
    }


def test_two_people_tagged_in_channel(notifs_dataset):
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": notifs_dataset["t"][1], "name": "chan1", "is_public": True},
    ).json()["channel_id"]
    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "u_id": notifs_dataset["id"][2],
        },
    )
    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "u_id": notifs_dataset["id"][0],
        },
    )
    requests.post(
        config.url + "message/send/v1",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "message": "@firstlast1 @firstlast aaa",
        },
    )
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][2],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1]
                + " tagged you in chan1: @firstlast1 @firstla",
            },
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1] + " added you to chan1",
            },
        ]
    }
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][0],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1]
                + " tagged you in chan1: @firstlast1 @firstla",
            },
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1] + " added you to chan1",
            },
        ]
    }


def test_not_a_tag(notifs_dataset):
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": notifs_dataset["t"][1], "name": "chan1", "is_public": True},
    ).json()["channel_id"]
    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "u_id": notifs_dataset["id"][2],
        },
    )
    requests.post(
        config.url + "message/send/v1",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "message": "firstlast1 @haha",
        },
    )
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][2],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": notifs_dataset["h"][1] + " added you to chan1",
            },
        ]
    }


def test_one_tag_dm(notifs_dataset):
    dm_id1 = requests.post(
        config.url + "dm/create/v1",
        json={
            "token": notifs_dataset["t"][1],
            "u_ids": [notifs_dataset["id"][0], notifs_dataset["id"][2]],
        },
    ).json()["dm_id"]
    requests.post(
        config.url + "message/senddm/v1",
        json={
            "token": notifs_dataset["t"][1],
            "dm_id": dm_id1,
            "message": "hahahaha@firstlast",
        },
    )
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][0],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": -1,
                "dm_id": dm_id1,
                "notification_message": notifs_dataset["h"][1]
                + " tagged you in firstlast, firstlast0, firstlast1: hahahaha@firstlast",
            },
            {
                "channel_id": -1,
                "dm_id": dm_id1,
                "notification_message": notifs_dataset["h"][1]
                + " added you to firstlast, firstlast0, firstlast1",
            },
        ]
    }


def test_one_react_channel(notifs_dataset):
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": notifs_dataset["t"][1], "name": "chan1", "is_public": True},
    ).json()["channel_id"]
    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "u_id": notifs_dataset["id"][2],
        },
    )
    msg_id1 = requests.post(
        config.url + "message/send/v1",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "message": "firstlast1 @haha",
        },
    ).json()["message_id"]
    requests.post(
        config.url + "message/react/v1",
        json={"token": notifs_dataset["t"][2], "message_id": msg_id1, "react_id": 1},
    )
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][1],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": chan_id1,
                "dm_id": -1,
                "notification_message": "firstlast1 reacted to your message in chan1",
            }
        ]
    }


def test_over_20_notifs(notifs_dataset):
    chan_id1 = requests.post(
        config.url + "channels/create/v2",
        json={"token": notifs_dataset["t"][1], "name": "chan1", "is_public": True},
    ).json()["channel_id"]
    requests.post(
        config.url + "channel/invite/v2",
        json={
            "token": notifs_dataset["t"][1],
            "channel_id": chan_id1,
            "u_id": notifs_dataset["id"][2],
        },
    )
    for i in range(25):
        requests.post(
            config.url + "message/send/v1",
            json={
                "token": notifs_dataset["t"][1],
                "channel_id": chan_id1,
                "message": str(i) + "@firstlast1 @haha",
            },
        )
    response = requests.get(
        config.url + "notifications/get/v1",
        params={
            "token": notifs_dataset["t"][2],
        },
    )
    assert response.json() == {
        "notifications": [
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 24@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 23@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 22@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 21@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 20@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 19@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 18@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 17@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 16@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 15@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 14@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 13@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 12@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 11@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 10@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 9@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 8@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 7@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 6@firstlast1 @haha",
            },
            {
                "channel_id": 0,
                "dm_id": -1,
                "notification_message": "firstlast0 tagged you in chan1: 5@firstlast1 @haha",
            },
        ]
    }
