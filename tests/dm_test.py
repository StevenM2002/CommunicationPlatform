import pytest
import requests
from src import config
from src.error import AccessError, InputError


@pytest.fixture
def dm_users():
    requests.delete(config.url + "clear/v1")

    user_1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "first1",
            "name_last": "last1",
        },
    ).json()
    user_2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome",
            "name_first": "first2",
            "name_last": "last2",
        },
    ).json()
    user_3 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow3@wow.com",
            "password": "awesome",
            "name_first": "first3",
            "name_last": "last3",
        },
    ).json()
    return [user_1, user_2, user_3]


@pytest.fixture
def dm_create(dm_users):
    dm_id = requests.post(
        f"{config.url}dm/create/v1",
        json={
            "token": dm_users[0]["token"],
            "u_ids": [i["auth_user_id"] for i in dm_users],
        },
    ).json()["dm_id"]
    return dm_id, dm_users


def test_create(dm_users):
    r = requests.post(
        f"{config.url}dm/create/v1",
        json={
            "token": dm_users[0]["token"],
            "u_ids": [i["auth_user_id"] for i in dm_users],
        },
    )
    assert r.status_code == 200
    assert type(r.json()["dm_id"]) == int


def test_list(dm_create):
    dm_users = dm_create[1]

    r = requests.get(f"{config.url}dm/list/v1", params={"token": dm_users[0]["token"]})

    assert r.status_code == 200
    assert r.json()["dms"] == [
        {"name": "first1last1, first2last2, first3last3", "dm_id": 0}
    ]


def test_remove(dm_create):
    dm_id, dm_users = dm_create

    r = requests.delete(
        f"{config.url}dm/remove/v1",
        json={
            "token": dm_users[0]["token"],
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    for user in dm_users:
        r = requests.get(f"{config.url}dm/list/v1", params={"token": user["token"]})
        assert r.status_code == 200
        assert r.json()["dms"] == []

        r = requests.get(
            f"{config.url}dm/details/v1",
            params={
                "token": user["token"],
                "dm_id": dm_id,
            },
        )
        assert r.status_code == InputError.code


def test_details(dm_create):
    dm_id, dm_users = dm_create

    r = requests.get(
        f"{config.url}dm/details/v1",
        params={
            "token": dm_users[0]["token"],
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200
    assert r.json() == {
        "name": "first1last1, first2last2, first3last3",
        "members": [
            {
                "email": "wow1@wow.com",
                "handle_str": "first1last1",
                "name_first": "first1",
                "name_last": "last1",
                "u_id": 0,
            },
            {
                "email": "wow2@wow.com",
                "handle_str": "first2last2",
                "name_first": "first2",
                "name_last": "last2",
                "u_id": 1,
            },
            {
                "email": "wow3@wow.com",
                "handle_str": "first3last3",
                "name_first": "first3",
                "name_last": "last3",
                "u_id": 2,
            },
        ],
    }


def test_leave(dm_create):
    dm_id, dm_users = dm_create

    r = requests.post(
        f"{config.url}dm/leave/v1",
        json={
            "token": dm_users[1]["token"],
            "dm_id": dm_id,
        },
    )
    assert r.status_code == 200

    r = requests.get(f"{config.url}dm/list/v1", params={"token": dm_users[1]["token"]})
    assert r.status_code == 200
    assert r.json()["dms"] == []

    r = requests.get(
        f"{config.url}dm/details/v1",
        params={
            "token": dm_users[1]["token"],
            "dm_id": dm_id,
        },
    )
    assert r.status_code == AccessError.code


def test_messages(dm_create):
    dm_id, dm_users = dm_create

    r = requests.get(
        f"{config.url}dm/messages/v1",
        params={
            "token": dm_users[0]["token"],
            "dm_id": dm_id,
            "start": 0,
        },
    )
    assert r.status_code == 200
    assert r.json() == {"messages": [], "start": 0, "end": -1}


def test_messages_bad_index(dm_create):
    dm_id, dm_users = dm_create

    r = requests.get(
        f"{config.url}dm/messages/v1",
        params={
            "token": dm_users[0]["token"],
            "dm_id": dm_id,
            "start": 10,
        },
    )
    assert r.status_code == InputError.code


def test_invalid_token(dm_users):

    requests.post(f"{config.url}auth/logout/v1", json={"token": dm_users[0]["token"]})

    r = requests.post(
        f"{config.url}dm/create/v1",
        json={
            "token": dm_users[0]["token"],
            "u_ids": [i["auth_user_id"] for i in dm_users],
        },
    )
    assert r.status_code == AccessError.code

    r = requests.get(
        f"{config.url}dm/list/v1",
        params={
            "token": dm_users[0]["token"],
        },
    )
    assert r.status_code == AccessError.code

    r = requests.delete(
        f"{config.url}dm/remove/v1",
        json={
            "token": dm_users[0]["token"],
            "dm_id": 0,
        },
    )
    assert r.status_code == AccessError.code

    r = requests.get(
        f"{config.url}dm/details/v1",
        params={
            "token": dm_users[0]["token"],
            "dm_id": 0,
        },
    )
    assert r.status_code == AccessError.code

    r = requests.post(
        f"{config.url}dm/leave/v1",
        json={
            "token": dm_users[0]["token"],
            "dm_id": 0,
        },
    )
    assert r.status_code == AccessError.code

    r = requests.get(
        f"{config.url}dm/messages/v1",
        params={"token": dm_users[0]["token"], "dm_id": 0, "start": 0},
    )
    assert r.status_code == AccessError.code


def test_all_leave(dm_create):
    dm_id, dm_users = dm_create

    for user in dm_users:
        r = requests.post(
            f"{config.url}dm/leave/v1",
            json={
                "token": user["token"],
                "dm_id": dm_id,
            },
        )
        assert r.status_code == 200


def test_unauthorised_remove(dm_create):
    dm_id, dm_users = dm_create
    r = requests.delete(
        f"{config.url}dm/remove/v1",
        json={
            "token": dm_users[2]["token"],
            "dm_id": dm_id,
        },
    )
    assert r.status_code == AccessError.code


def test_invalid_id_create(dm_users):
    r = requests.post(
        f"{config.url}dm/create/v1",
        json={
            "token": dm_users[0]["token"],
            "u_ids": [i["auth_user_id"] for i in dm_users] + [400],
        },
    )
    assert r.status_code == InputError.code


def test_invalid_dm_id(dm_users):
    r = requests.delete(
        f"{config.url}dm/remove/v1",
        json={
            "token": dm_users[0]["token"],
            "dm_id": 100,
        },
    )
    assert r.status_code == InputError.code

    r = requests.get(
        f"{config.url}dm/details/v1",
        params={
            "token": dm_users[0]["token"],
            "dm_id": 100,
        },
    )
    assert r.status_code == InputError.code

    r = requests.post(
        f"{config.url}dm/leave/v1",
        json={
            "token": dm_users[1]["token"],
            "dm_id": 100,
        },
    )
    assert r.status_code == InputError.code

    r = requests.get(
        f"{config.url}dm/messages/v1",
        params={
            "token": dm_users[0]["token"],
            "dm_id": 100,
            "start": 0,
        },
    )
    assert r.status_code == InputError.code


def test_create_mutiple_dm(dm_users):
    ids = []
    for _ in range(10):
        r = requests.post(
            f"{config.url}dm/create/v1",
            json={
                "token": dm_users[0]["token"],
                "u_ids": [i["auth_user_id"] for i in dm_users],
            },
        )
        assert r.status_code == 200
        assert type(r.json()["dm_id"]) == int
        ids.append(r.json()["dm_id"])

    assert len(ids) == len(set(ids))
    assert len(ids) == 10


def test_not_in_dm(dm_users):
    dm_id = requests.post(
        f"{config.url}dm/create/v1",
        json={
            "token": dm_users[0]["token"],
            "u_ids": [i["auth_user_id"] for i in dm_users[:2]],
        },
    ).json()["dm_id"]

    r = requests.delete(
        f"{config.url}dm/remove/v1",
        json={
            "token": dm_users[2]["token"],
            "dm_id": dm_id,
        },
    )
    assert r.status_code == AccessError.code

    r = requests.post(
        f"{config.url}dm/leave/v1",
        json={
            "token": dm_users[2]["token"],
            "dm_id": dm_id,
        },
    )
    assert r.status_code == AccessError.code
    r = requests.get(
        f"{config.url}dm/messages/v1",
        params={
            "token": dm_users[2]["token"],
            "dm_id": dm_id,
            "start": 0,
        },
    )
    assert r.status_code == AccessError.code
