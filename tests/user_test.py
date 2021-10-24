import json
import requests
import pytest
from src import config
from src.auth import auth_register_v2

OK = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403


@pytest.fixture
def new_users():
    # Clears the data store
    requests.delete(f"{config.url}/clear/v1")
    # Creates a user with id 0
    user = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "mario@gmail.com",
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


# users/all/v1 tests
# Checks that an invalid token will return an Access Error
def test_all_invalid_token(new_users):
    response = requests.get(
        f"{config.url}/users/all/v1", params={"token": "awsfkhbaeikfnkjasn"}
    )
    assert response.status_code == ACCESS_ERROR


# Checks that when one user is entered the correct list is returned
def test_all_single_user():
    requests.delete(f"{config.url}/clear/v1")
    token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "mario@gmail.com",
            "password": "itsameeee",
            "name_first": "Mario",
            "name_last": "Plumber",
        },
    ).json()["token"]
    response = requests.get(f"{config.url}/users/all/v1", params={"token": token})
    assert response.status_code == OK
    assert response.json()['users'] == [
        {
            "u_id": 0,
            "email": "mario@gmail.com",
            "name_first": "Mario",
            "name_last": "Plumber",
            "handle_str": "marioplumber",
        }
    ]


# Checks that when multiple users are added the correct list is returned
def test_all_valid_users(new_users):
    response = requests.get(f"{config.url}/users/all/v1", params={"token": new_users})
    assert response.status_code == OK
    assert response.json()['users'] == [
        {
            "u_id": 0,
            "email": "mario@gmail.com",
            "name_first": "Mario",
            "name_last": "Plumber",
            "handle_str": "marioplumber",
        },
        {
            "u_id": 1,
            "email": "luigi@gmail.com",
            "name_first": "Luigi",
            "name_last": "Plumber",
            "handle_str": "luigiplumber",
        },
        {
            "u_id": 2,
            "email": "Peach@gmail.com",
            "name_first": "Princess",
            "name_last": "Peach",
            "handle_str": "princesspeach",
        },
        {
            "u_id": 3,
            "email": "bowser@gmail.com",
            "name_first": "Bowser",
            "name_last": "Turtle",
            "handle_str": "bowserturtle",
        },
    ]


# user/profile/v1 tests
# Checks if the channel_id doesn't point to a valid user, an input error is raised
def test_profile_invalid_user(new_users):
    response = requests.get(
        f"{config.url}/user/profile/v1", params={"token": new_users, "u_id": 20}
    )
    assert response.status_code == INPUT_ERROR


# Checks if an invalid token is inserted, an access error is returned
def test_profile_invalid_token(new_users):
    response = requests.get(
        f"{config.url}/user/profile/v1",
        params={"token": "awsfkhbaeikfnkjasn", "u_id": 0},
    )
    assert response.status_code == ACCESS_ERROR


# Checks that when a valid profile is input, the correct user's profile is output
def test_profile_valid_id(new_users):
    response = requests.get(
        f"{config.url}/user/profile/v1", params={"token": new_users, "u_id": 1}
    )
    assert response.status_code == OK
    assert response.json()['user'] == {
        "u_id": 1,
        "email": "luigi@gmail.com",
        "name_first": "Luigi",
        "name_last": "Plumber",
        "handle_str": "luigiplumber",
    }


# Checks if a one calls themselves, it still returns the user information
def test_profile_valid_self(new_users):
    response = requests.get(
        f"{config.url}/user/profile/v1", params={"token": new_users, "u_id": 0}
    )
    assert response.status_code == OK
    assert response.json()['user'] == {
        "u_id": 0,
        "email": "mario@gmail.com",
        "name_first": "Mario",
        "name_last": "Plumber",
        "handle_str": "marioplumber",
    }


# user/profile/setname/v1
# Checks that an invalid token returns an Access Error
def test_setname_invalid_id(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setname/v1",
        json={
            "token": "asdhujbfgsdshjadng",
            "name_first": "toad",
            "name_last": "mushroom",
        },
    )
    assert response.status_code == ACCESS_ERROR


# Checks that a short first name returns an input error
def test_setname_short_first(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setname/v1",
        json={"token": new_users, "name_first": "", "name_last": "mushroom"},
    )
    assert response.status_code == INPUT_ERROR


# Checks that a short last name returns an input error
def test_setname_short_last(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setname/v1",
        json={"token": new_users, "name_first": "toad", "name_last": ""},
    )
    assert response.status_code == INPUT_ERROR


# Checks that a long first name returns an input error
def test_setname_long_first(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setname/v1",
        json={
            "token": new_users,
            "name_first": "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm",
            "name_last": "mushroom",
        },
    )
    assert response.status_code == INPUT_ERROR


# Checks that a long last name returns an input error
def test_setname_long_last(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setname/v1",
        json={
            "token": new_users,
            "name_first": "toad",
            "name_last": "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm",
        },
    )
    assert response.status_code == INPUT_ERROR


# Checks that a valid input creates the expected change
def test_setname_valid(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setname/v1",
        json={"token": new_users, "name_first": "Toad", "name_last": "Mushroom"},
    )
    assert response.status_code == OK
    assert response.json() == {}
    new_response = requests.get(
        f"{config.url}/user/profile/v1", params={"token": new_users, "u_id": 0}
    )
    assert new_response.status_code == OK
    assert new_response.json()['user'] == {
        "u_id": 0,
        "email": "mario@gmail.com",
        "name_first": "Toad",
        "name_last": "Mushroom",
        "handle_str": "marioplumber",
    }


# user/profile/setemail/v1 test
# Checks that an invalid token returns an Access Error
def test_setemail_invalid_id(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setemail/v1",
        json={
            "token": "asdhujbfgsdshjadng",
            "email": "toad@gmail.com",
        },
    )
    assert response.status_code == ACCESS_ERROR


# Checks that an invalid email returns an Input Error
def test_setemail_invalid_email(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setemail/v1",
        json={
            "token": new_users,
            "email": "toadedoesntlikeemails",
        },
    )
    assert response.status_code == INPUT_ERROR


# Checks that a duplicate email returns an Input Error
def test_setemail_duplicate_email(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setemail/v1",
        json={
            "token": new_users,
            "email": "bowser@gmail.com",
        },
    )
    assert response.status_code == INPUT_ERROR


# Checks that a valid email returns the correct output
def test_setemail_valid(new_users):
    response = requests.put(
        f"{config.url}/user/profile/setemail/v1",
        json={
            "token": new_users,
            "email": "toad@gmail.com",
        },
    )
    assert response.status_code == OK
    assert response.json() == {}
    new_response = requests.get(
        f"{config.url}/user/profile/v1", params={"token": new_users, "u_id": 0}
    )
    assert new_response.status_code == OK
    assert new_response.json()['user'] == {
        "u_id": 0,
        "email": "toad@gmail.com",
        "name_first": "Mario",
        "name_last": "Plumber",
        "handle_str": "marioplumber",
    }


# user/profile/sethandle/v1 test
# Checks that an invalid token returns an Access Error
def test_sethandle_invalid_id(new_users):
    response = requests.put(
        f"{config.url}/user/profile/sethandle/v1",
        json={
            "token": "asdhujbfgsdshjadng",
            "handle_str": "toadmushroom",
        },
    )
    assert response.status_code == ACCESS_ERROR


# Checks that a short handle returns an Input Error
def test_sethandle_short(new_users):
    response = requests.put(
        f"{config.url}/user/profile/sethandle/v1",
        json={
            "token": new_users,
            "handle_str": "ab",
        },
    )
    assert response.status_code == INPUT_ERROR


# Checks that a long handle returns an Input Error
def test_sethandle_long(new_users):
    response = requests.put(
        f"{config.url}/user/profile/sethandle/v1",
        json={
            "token": new_users,
            "handle_str": "qwertyuiopasdfghjklzxcvbnm",
        },
    )
    assert response.status_code == INPUT_ERROR


# Checks that a handle doesn't contain non alpha-numeric characters
def test_sethandle_alphanumeric(new_users):
    response = requests.put(
        f"{config.url}/user/profile/sethandle/v1",
        json={
            "token": new_users,
            "handle_str": "toaddon'tlike??",
        },
    )
    assert response.status_code == INPUT_ERROR


# Checks that handle is in use, returning an Inpur Error
def test_sethandle_duplicate(new_users):
    response = requests.put(
        f"{config.url}/user/profile/sethandle/v1",
        json={
            "token": new_users,
            "handle_str": "luigiplumber",
        },
    )
    assert response.status_code == INPUT_ERROR


# Checks that a valid email returns the correct output
def test_sethandle_valid(new_users):
    response = requests.put(
        f"{config.url}/user/profile/sethandle/v1",
        json={
            "token": new_users,
            "handle_str": "toadmushroom",
        },
    )
    assert response.status_code == OK
    assert response.json() == {}
    new_response = requests.get(
        f"{config.url}/user/profile/v1", params={"token": new_users, "u_id": 0}
    )
    assert new_response.status_code == OK
    assert new_response.json()['user'] == {
        "u_id": 0,
        "email": "mario@gmail.com",
        "name_first": "Mario",
        "name_last": "Plumber",
        "handle_str": "toadmushroom",
    }
