import json
import requests
from auth import auth_register_v2

OK = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403


@pytest_fixture
def new_users():
    # Clears the data store
    requests.delete(f"{config.url}/clear/v1")
    # Creates a user with id 0
    user = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "mario@gmail.com@gmail.com",
            "password": "itsameeee",
            "name_first": "Mario",
            "name_last": "Plumber",
        },
    )
    user_token = user.json()["token"]
    # Creates three new users
    requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "luigi@gmail.com",
            "password": "itsameee",
            "name_first": "Luigi",
            "name_last": "Plumber",
        },
    )
    requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "Peach@gmail.com",
            "password": "password",
            "name_first": "Princess",
            "name_last": "Peach",
        },
    )
    requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "bowser@gmail.com",
            "password": "wuahahaha",
            "name_first": "Bowser",
            "name_last": "Turtle",
        },
    )
    return user_token

# Checks that an invalid token will return an Access Error
def test_invalid_token(new_users):
    response = requests.get(f"{config.url}/user/all/v1", params={"token" = "awsfkhbaeikfnkjasn"})
    assert response.status_code == ACCESS_ERROR

# Checks that when one user is entered the correct list is returned
def test_single_user():
    requests.delete(f"{config.url}/clear/v1")
    token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "mario@gmail.com@gmail.com",
            "password": "itsameeee",
            "name_first": "Mario",
            "name_last": "Plumber",
        },
    ).json()["token"]
    response = requests.get(f"{config.url}/user/all/v1", params={"token": token})
    assert reponse.status_code == OK
    assert reponse.json() == []


# Checks that when multiple users are added the correct list is returned
def test_valid_users(new_users):
    response = requests.get(f"{config.url}/user/all/v1", params={new_users})
    assert response.status_code == OK
    assert response.json(){
        [
            {
            "email": "mario@gmail.com",
            "name_first": "Mario",
            "name_last": "Plumber",
            "handle_str": "marioplumber",

        },
        {
            "email": "luigi@gmail.com",
            "name_first": "Luigi",
            "name_last": "Plumber",
            "handle_str": "luigiplumber"
        },
        {
            "email": "Peach@gmail.com",
            "name_first": "Princess",
            "name_last": "Peach",
            "handle_str": "princesspeach"
        },
        {
            "email": "bowser@gmail.com",
            "name_first": "Bowser",
            "name_last": "Turtle",
            "handle_str": "bowserturtle"
        }
        ]
    }