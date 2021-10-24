"""Tests for functions from src/auth.py"""
import requests
from src import config
from src.error import AccessError, InputError


def test_login():
    requests.delete(f"{config.url}clear/v1")

    r = requests.post(
        f"{config.url}auth/register/v2",
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
        f"{config.url}auth/login/v2",
        json={"email": "wow@wow.com", "password": "awesome"},
    )
    assert r.status_code == 200
    assert r.json()["auth_user_id"] == auth_user_id


def test_wrong_login():
    requests.delete(f"{config.url}clear/v1")

    r = requests.post(
        f"{config.url}auth/login/v2",
        json={"email": "wow@wow.com", "password": "awesome"},
    )
    assert r.status_code == InputError.code
    assert r.json()["message"] == "<p>email and or password was incorrect</p>"


def test_incorrect_password():
    requests.delete(f"{config.url}clear/v1")

    requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    )

    r = requests.post(
        f"{config.url}auth/login/v2",
        json={"email": "wow@wow.com", "password": "notawesome"},
    )
    assert r.status_code == InputError.code
    assert r.json()["message"] == "<p>email and or password was incorrect</p>"


def test_invalid_register():
    requests.delete(f"{config.url}clear/v1")
    # password < 6 charecters
    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "no",
            "name_first": "first",
            "name_last": "last",
        },
    )
    assert r.status_code == InputError.code
    assert r.json()["message"] == "<p>password must be 6 or more characters long</p>"

    requests.delete(f"{config.url}clear/v1")
    # too short firstname
    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "",
            "name_last": "last",
        },
    )
    assert r.status_code == InputError.code
    assert (
        r.json()["message"] == "<p>first name must be between 1 and 50 characters</p>"
    )

    requests.delete(f"{config.url}clear/v1")
    # too long firstname
    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "thisnameislongerthan50charecterslongthisnameislongerthan50charecterslong",
            "name_last": "last",
        },
    )
    assert r.status_code == InputError.code
    assert (
        r.json()["message"] == "<p>first name must be between 1 and 50 characters</p>"
    )

    requests.delete(f"{config.url}clear/v1")
    # too short lastname
    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "first",
            "name_last": "",
        },
    )
    assert r.status_code == InputError.code
    assert r.json()["message"] == "<p>last name must be between 1 and 50 characters</p>"

    requests.delete(f"{config.url}clear/v1")
    # too long lastname
    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "first",
            "name_last": "thisnameislongerthan50charecterslongthisnameislongerthan50charecterslong",
        },
    )
    assert r.status_code == InputError.code
    assert r.json()["message"] == "<p>last name must be between 1 and 50 characters</p>"

    requests.delete(f"{config.url}clear/v1")
    # incorrect email
    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "ow.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    )
    assert r.status_code == InputError.code
    assert r.json()["message"] == "<p>invalid email</p>"


def test_existing_email():
    requests.delete(f"{config.url}clear/v1")
    # incorrect email
    requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password",
            "name_first": "first",
            "name_last": "last",
        },
    )

    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "password2",
            "name_first": "first2",
            "name_last": "last2",
        },
    )
    assert r.status_code == InputError.code
    assert r.json()["message"] == "<p>email already belongs to a user</p>"


def test_existing_handle():
    requests.delete(f"{config.url}clear/v1")

    user0 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    user1 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()
    user2 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()

    test_channel = requests.post(
        f"{config.url}channels/create/v2",
        json={"token": user0["token"], "name": "test", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        f"{config.url}channel/join/v2",
        json={"token": user1["token"], "channel_id": test_channel},
    )

    requests.post(
        f"{config.url}channel/join/v2",
        json={"token": user2["token"], "channel_id": test_channel},
    )

    users = requests.get(
        f"{config.url}channel/details/v2",
        params={"token": user0["token"], "channel_id": test_channel},
    ).json()["all_members"]

    for user in users:
        if user["u_id"] == user1["auth_user_id"]:
            assert user["handle_str"] == "firstlast0"
        if user["u_id"] == user2["auth_user_id"]:
            assert user["handle_str"] == "firstlast1"


def test_multiple_register():
    requests.delete(f"{config.url}clear/v1")

    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    )
    assert r.status_code == 200
    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome2",
            "name_first": "first2",
            "name_last": "last2",
        },
    )
    assert r.status_code == 200
    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome1",
            "name_first": "first1",
            "name_last": "last1",
        },
    )
    assert r.status_code == 200


def test_multiple_id():
    requests.delete(f"{config.url}clear/v1")

    id1 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["auth_user_id"]
    id2 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["auth_user_id"]
    id3 = requests.post(
        f"{config.url}auth/register/v2",
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
    # return
    requests.delete(f"{config.url}clear/v1")

    user0 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "firstverylongname",
            "name_last": "lastname",
        },
    ).json()
    user1 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "firstverylongname",
            "name_last": "lastname",
        },
    ).json()
    user2 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome",
            "name_first": "firstverylongname",
            "name_last": "lastname",
        },
    ).json()

    test_channel = requests.post(
        f"{config.url}channels/create/v2",
        json={"token": user0["token"], "name": "test", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        f"{config.url}channel/join/v2",
        json={"token": user1["token"], "channel_id": test_channel},
    )

    requests.post(
        f"{config.url}channel/join/v2",
        json={"token": user2["token"], "channel_id": test_channel},
    )

    users = requests.get(
        f"{config.url}channel/details/v2",
        params={"token": user0["token"], "channel_id": test_channel},
    ).json()["all_members"]

    for user in users:
        if user["u_id"] == user0["auth_user_id"]:
            assert user["handle_str"] == "firstverylongnamelas"
        if user["u_id"] == user1["auth_user_id"]:
            assert user["handle_str"] == "firstverylongnamelas0"
        if user["u_id"] == user2["auth_user_id"]:
            assert user["handle_str"] == "firstverylongnamelas1"


def test_non_alphanumeric_handle():
    requests.delete(f"{config.url}clear/v1")

    user0 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "hello👍?!",
            "name_last": "//@!wow",
        },
    ).json()
    user1 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "👍?!",
            "name_last": "//@!",
        },
    ).json()
    user2 = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow2@wow.com",
            "password": "awesome",
            "name_first": "👍?!",
            "name_last": "//@!",
        },
    ).json()

    test_channel = requests.post(
        f"{config.url}channels/create/v2",
        json={"token": user0["token"], "name": "test", "is_public": True},
    ).json()["channel_id"]

    requests.post(
        f"{config.url}channel/join/v2",
        json={"token": user1["token"], "channel_id": test_channel},
    )

    requests.post(
        f"{config.url}channel/join/v2",
        json={"token": user2["token"], "channel_id": test_channel},
    )

    users = requests.get(
        f"{config.url}channel/details/v2",
        params={"token": user0["token"], "channel_id": test_channel},
    ).json()["all_members"]

    for user in users:
        if user["u_id"] == user0["auth_user_id"]:
            assert user["handle_str"] == "hellowow"
        if user["u_id"] == user1["auth_user_id"]:
            assert user["handle_str"] == "0"
        if user["u_id"] == user2["auth_user_id"]:
            assert user["handle_str"] == "1"


def test_logout():
    requests.delete(f"{config.url}clear/v1")

    r = requests.post(
        f"{config.url}auth/register/v2",
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
        f"{config.url}auth/logout/v1",
        json={"token": token},
    )
    assert r.status_code == 200

    r = requests.get(
        f"{config.url}channels/list/v2",
        json={
            "token": token,
        },
    )
    assert r.status_code == AccessError.code


def test_logout_multiple():
    requests.delete(f"{config.url}clear/v1")

    tokens = []
    for i in range(10):

        r = requests.post(
            f"{config.url}auth/register/v2",
            json={
                "email": f"{i}wow@wow.com",
                "password": "awesome",
                "name_first": "first",
                "name_last": "last",
            },
        )
        assert r.status_code == 200
        tokens.append(r.json()["token"])

    tokens.reverse()
    for token in tokens:
        r = requests.post(
            f"{config.url}auth/logout/v1",
            json={"token": token},
        )
        assert r.status_code == 200

        r = requests.get(
            f"{config.url}channels/list/v2",
            json={
                "token": token,
            },
        )
        assert r.status_code == AccessError.code


def test_logout_2x():
    requests.delete(f"{config.url}clear/v1")

    r = requests.post(
        f"{config.url}auth/register/v2",
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
        f"{config.url}auth/logout/v1",
        json={"token": token},
    )
    assert r.status_code == 200

    r = requests.post(
        f"{config.url}auth/logout/v1",
        json={"token": token},
    )
    assert r.status_code == AccessError.code

    r = requests.get(
        f"{config.url}channels/list/v2",
        json={
            "token": token,
        },
    )
    assert r.status_code == AccessError.code


def test_logout_removed_user():
    requests.delete(f"{config.url}clear/v1")

    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    )
    token_owner = r.json()["token"]

    r = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow1@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    )
    u_id = r.json()["auth_user_id"]
    user_token = r.json()["token"]

    r = requests.delete(
        f"{config.url}admin/user/remove/v1", json={"token": token_owner, "u_id": u_id}
    )
    assert r.status_code == 200

    r = requests.post(
        f"{config.url}auth/logout/v1",
        json={"token": user_token},
    )
    assert r.status_code == AccessError.code

    r = requests.get(
        f"{config.url}channels/list/v2",
        params={
            "token": user_token,
        },
    )
    assert r.status_code == AccessError.code
