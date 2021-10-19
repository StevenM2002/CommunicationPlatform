"""Tests for functions from src/auth.py"""
import pytest
import requests
from src import config


def test_login():
    requests.delete(config.url + "clear/v1")

    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    )
    assert r.status_code == 200
    auth_user_id = r.json()["auth_user_id"]

    r = requests.post(
        config.url + "auth/login/v2",
        json={"email": "wow@wow.com", "password": "awesome"},
    )
    assert r.status_code == 200
    assert r.json()["auth_user_id"] == auth_user_id


def test_wrong_login():
    requests.delete(config.url + "clear/v1")

    r = requests.post(
        config.url + "auth/login/v2",
        json={"email": "wow@wow.com", "password": "awesome"},
    )
    assert r.status_code == 400
    assert r.json()["message"] == "<p>email and or password was incorrect</p>"


def test_invalid_register():
    requests.delete(config.url + "clear/v1")
    # password < 6 charecters
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "no",
            "name_first": "first",
            "name_last": "last",
        },
    )
    assert r.status_code == 400
    assert r.json()["message"] == "<p>password must be 6 or more characters long</p>"

    requests.delete(config.url + "clear/v1")
    # too short firstname
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "",
            "name_last": "last",
        },
    )
    assert r.status_code == 400
    assert (
        r.json()["message"] == "<p>first name must be between 1 and 50 characters</p>"
    )

    requests.delete(config.url + "clear/v1")
    # too long firstname
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "thisnameislongerthan50charecterslongthisnameislongerthan50charecterslong",
            "name_last": "last",
        },
    )
    assert r.status_code == 400
    assert (
        r.json()["message"] == "<p>first name must be between 1 and 50 characters</p>"
    )

    requests.delete(config.url + "clear/v1")
    # too short lastname
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "first",
            "name_last": "",
        },
    )
    assert r.status_code == 400
    assert r.json()["message"] == "<p>last name must be between 1 and 50 characters</p>"

    requests.delete(config.url + "clear/v1")
    # too long lastname
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "first",
            "name_last": "thisnameislongerthan50charecterslongthisnameislongerthan50charecterslong",
        },
    )
    assert r.status_code == 400
    assert r.json()["message"] == "<p>last name must be between 1 and 50 characters</p>"

    #     # too long lastname
    #     with pytest.raises(InputError):
    #         assert auth_register_v1(
    #             "wow@wow.com",
    #             "password",
    #             "first",
    #             "thisnameislongerthan50charecterslongthisnameislongerthan50charecterslong",
    #         )
    #     clear_v1()

    requests.delete(config.url + "clear/v1")
    # incorrect email
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "ow.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    )
    assert r.status_code == 400
    assert r.json()["message"] == "<p>invalid email</p>"


def test_existing_email():
    requests.delete(config.url + "clear/v1")
    # incorrect email
    requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    )

    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password2",
            "name_first": "first2",
            "name_last": "last2",
        },
    )
    print(r.json())
    assert r.status_code == 400
    assert r.json()["message"] == "<p>email already belongs to a user</p>"


def test_existing_handle():
    requests.delete(config.url + "clear/v1")

    user0 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    user1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    user2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()

    test_channel = requests.post(
        config.url + "channels/create/v2",
        json={"token": user0["token"], "name": "test", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        config.url + "channels/join/v2",
        json={"token": user1["token"], "channel_id": test_channel},
    )

    requests.post(
        config.url + "channels/join/v2",
        json={"token": user2["token"], "channel_id": test_channel},
    )

    users = requests.post(
        config.url + "channels/details/v2",
        json={"token": user0["token"], "channel_id": test_channel},
    ).json()["all_members"]

    for user in users:
        if user["u_id"] == user1["auth_user_id"]:
            assert user["handle_str"] == "firstlast0"
        if user["u_id"] == user2["auth_user_id"]:
            assert user["handle_str"] == "firstlast1"


def test_multiple_register():
    requests.delete(config.url + "clear/v1")

    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    )
    assert r.status_code == 200
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome2",
            "name_first": "first2",
            "name_last": "last2",
        },
    )
    assert r.status_code == 200
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome1",
            "name_first": "first1",
            "name_last": "last1",
        },
    )
    assert r.status_code == 200


def test_multiple_id():
    requests.delete(config.url + "clear/v1")

    id1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["auth_user_id"]
    id2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["auth_user_id"]
    id3 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["auth_user_id"]

    assert id1 != id2
    assert id2 != id3
    assert id1 != id3


def test_max_length_handle():
    requests.delete(config.url + "clear/v1")

    user0 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "firstverylongname",
            "name_last": "lastname",
        },
    ).json()
    user1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "firstverylongname",
            "name_last": "lastname",
        },
    ).json()
    user2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome",
            "name_first": "firstverylongname",
            "name_last": "lastname",
        },
    ).json()

    test_channel = requests.post(
        config.url + "channels/create/v2",
        json={"token": user0["token"], "name": "test", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        config.url + "channels/join/v2",
        json={"token": user1["token"], "channel_id": test_channel},
    )

    requests.post(
        config.url + "channels/join/v2",
        json={"token": user2["token"], "channel_id": test_channel},
    )

    users = requests.post(
        config.url + "channels/details/v2",
        json={"token": user0["token"], "channel_id": test_channel},
    ).json()["all_members"]

    for user in users:
        if user["u_id"] == user0["auth_user_id"]:
            assert user["handle_str"] == "firstverylongnamelas0"
        if user["u_id"] == user1["auth_user_id"]:
            assert user["handle_str"] == "firstverylongnamelas1"
        if user["u_id"] == user2["auth_user_id"]:
            assert user["handle_str"] == "firstverylongnamelas"


def test_non_alphanumeric_handle():
    requests.delete(config.url + "clear/v1")

    user0 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "hello👍?!",
            "name_last": "//@!wow",
        },
    ).json()
    user1 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "👍?!",
            "name_last": "//@!",
        },
    ).json()
    user2 = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome",
            "name_first": "👍?!",
            "name_last": "//@!",
        },
    ).json()

    test_channel = requests.post(
        config.url + "channels/create/v2",
        json={"token": user0["token"], "name": "test", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        config.url + "channels/join/v2",
        json={"token": user1["token"], "channel_id": test_channel},
    )

    requests.post(
        config.url + "channels/join/v2",
        json={"token": user2["token"], "channel_id": test_channel},
    )

    users = requests.post(
        config.url + "channels/details/v2",
        json={"token": user0["token"], "channel_id": test_channel},
    ).json()["all_members"]

    for user in users:
        if user["u_id"] == user0["auth_user_id"]:
            assert user["handle_str"] == "hellowow"
        if user["u_id"] == user1["auth_user_id"]:
            assert user["handle_str"] == "0"
        if user["u_id"] == user2["auth_user_id"]:
            assert user["handle_str"] == "1"


def test_logout():
    requests.delete(config.url + "clear/v1")

    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    )
    assert r.status_code == 200
    token = r.json()["token"]

    r = requests.post(
        config.url + "auth/logout/v1",
        json={"token": token},
    )
    assert r.status_code == 200

    r = requests.post(
        config.url + "channels/list/v2",
        json={
            "token": token,
        },
    )
    assert r.status_code == 400
