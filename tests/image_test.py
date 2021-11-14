from src.error import InputError
import requests
from src import config

test_url = "http://i.postimg.cc/FRGqQfwC/Scanned-Document.jpg"
test_bad = "http://via.placeholder.com/350x150"


def test_image():
    requests.delete(f"{config.url}clear/v1")

    user = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]

    r = requests.post(
        f"{config.url}user/profile/uploadphoto/v1",
        json={
            "token": user,
            "img_url": test_url,
            "x_start": 0,
            "y_start": 0,
            "x_end": 100,
            "y_end": 130,
        },
    )
    assert r.status_code == 200

    user_data = requests.get(
        f"{config.url}users/all/v1", params={"token": user}
    ).json()["users"][0]

    r = requests.get(user_data["profile_img_url"])
    assert r.status_code == 200


def test_crop_too_large():
    requests.delete(f"{config.url}clear/v1")

    user = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]

    r = requests.post(
        f"{config.url}user/profile/uploadphoto/v1",
        json={
            "token": user,
            "img_url": test_url,
            "x_start": 0,
            "y_start": 0,
            "x_end": 100000,
            "y_end": 13000,
        },
    )
    assert r.status_code == InputError.code


def test_crop_bad_img():
    requests.delete(f"{config.url}clear/v1")

    user = requests.post(
        f"{config.url}auth/register/v2",
        json={
            "email": "wow@wow.com",
            "password": "awesome",
            "name_first": "first",
            "name_last": "last",
        },
    ).json()["token"]

    r = requests.post(
        f"{config.url}user/profile/uploadphoto/v1",
        json={
            "token": user,
            "img_url": test_bad,
            "x_start": 0,
            "y_start": 0,
            "x_end": 10,
            "y_end": 10,
        },
    )
    assert r.status_code == InputError.code
