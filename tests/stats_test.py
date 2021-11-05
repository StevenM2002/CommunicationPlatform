import math
import time

from src import config
from src.error import AccessError, InputError

import pytest
import requests


OK = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403


@pytest.fixture
def new_time():
    # Clears the Data Store and finds the timestamp of when the code was cleared
    timestamp = math.floor(time.time())
    requests.delete(f"{config.url}/clear/v1")
    # Initialises a new user
    user_timestamp = math.floor(time.time())
    token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "mario@gmail.com",
            "password": "itsameeee",
            "name_first": "Mario",
            "name_last": "Plumber",
        },
    )
    # Saves the timestamp and token to a new list
    data = {
        "timestamp": timestamp, 
        "token": token.json()["token"], 
        "user_timestamp": user_timestamp
        }
    return data


""" ========================= Workplace Stats Tests ========================="""
# Tests that when given an invalid token, an Access Error is raised
def test_workplace_invalid(new_time):
    response = requests.get(f"{config.url}/users/stats/v1", params={"token": "asdhgjjas"})
    assert response.status_code == ACCESS_ERROR

# Tests that the initialised values for workplace stats returns the correct value
def test_workplace_init(new_time):
    token = new_time["token"]
    timestamp = new_time["timestamp"]
    response = requests.get(f"{config.url}/users/stats/v1", params={"token": token})
    assert response.status_code == OK
    assert response == {
        "channels_exist": [{"num_channels_exist": 0, "time_stamp": timestamp}],
        "dms_exist": [{"num_dms_exist": 0, "time_stamp": timestamp}],
        "messages_exist": [{"num_messages_exist": 0, "time_stamp": timestamp}],
        "utilization_rate": 0,
    }


# Tests that a set of added channels, dms, and messages results in the correct stats
def test_workplace_stats(new_time):
    token = new_time["token"]
    timestamp = new_time["timestamp"]
    timestamps = []
    # Creating new channels, and making members join the channels
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": token,
            "name": "public_channel",
            "is_public": True,
        },
    )
    new_token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jane.citizen@gmail.com",
            "password": "password",
            "name_first": "Jane",
            "name_last": "Citizen",
        },
    )
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": token,
            "name": "second_channel",
            "is_public": True,
        },
    )
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": token,
            "name": "private_channel",
            "is_public": False,
        },
    )
    requests.post(
        f"{config.url}/channel/join/v2",
        json={"token": new_token.json()["token"], "channel_id": 0},
    )
    requests.post(
        f"{config.url}/channel/join/v2",
        json={"token": new_token.json()["token"], "channel_id": 1},
    )
    # Creates a new dm
    timestamps.append(math.floor(time.time))
    requests.get(f"{config.url}/dm/create/v1", json={"token": token, "u_ids": 1})
    # Sending messages in a channel
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config_url}/message/send/v1", 
        json={
            "token": token, 
            "channel_id": 0,
            "message": "Test Message"
            })
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config_url}/message/send/v1", 
        json={
            "token": token, 
            "channel_id": 0,
            "message": "Another Test Message"
            })
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config_url}/message/send/v1", 
        json={
            "token": token, 
            "channel_id": 0,
            "message": "A final test message"
    })
    response = requests.get(f"{config.url}/users/stats/v1", params={"token": token})
    assert response.status_code == OK
    assert response == {
        "channels_exist": [
            {"num_channels_exist": 3, "time_stamp": timestamps[2]},
            {"num_channels_exist": 2, "time_stamp": timestamps[1]},
            {"num_channels_exist": 1, "time_stamp": timestamps[0]},
            {"num_channels_exist": 0, "time_stamp": timestamp}],
        "dms_exist": [
            {"num_dms_exist": 1, "time_stamp": timestamps[3]},
            {"num_dms_exist": 0, "time_stamp": timestamp}],
        "messages_exist": [
            {"num_messages_exist": 3, "time_stamp": timestamps[6]},
            {"num_messages_exist": 2, "time_stamp": timestamps[5]},
            {"num_messages_exist": 1, "time_stamp": timestamps[4]},
            {"num_messages_exist": 0, "time_stamp": timestamp}],
        "utilization_rate": 1,
    }

""" =========================== User Stats Tests ==========================="""
# Tests that when given an invalid token, an Access Error is raised
def test_user_invalid(new_time):
    response = requests.get(f"{config.url}/user/stats/v1", params={"token": "asdhgjjas"})
    assert response.status_code == ACCESS_ERROR


# Tests that a new created user returns the correct involvement rate
def test_user_init(new_time):
    token = new_time["token"]
    timestamp = new_time["timestamp"]
    response = requests.get(f"{config.url}/user/stats/v1", params={"token": token})
    assert response.status_code == OK
    assert response == {
        "channels_joined": [{"num_channels_joined": "time_stamp": timestamp}],
        "dms_joined": [{"num_dms_joined": "time_stamp": timestamp}],
        "messages_sent": [{"num_messages_sent": "time_stamp": timestamp}],
        "involvement_rate": 0
    }


# Tests that a user added into channels, and sending messages and dms has the
# correctly calculated engagement value
def test_user_stats(new_time):
    token = new_time["token"]
    timestamp = new_time["timestamp"]
    timestamps = []
    # Creating new channels, and making members join the channels
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": token,
            "name": "public_channel",
            "is_public": True,
        },
    )
    new_token = requests.post(
        f"{config.url}/auth/register/v2",
        json={
            "email": "jane.citizen@gmail.com",
            "password": "password",
            "name_first": "Jane",
            "name_last": "Citizen",
        },
    )
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": token,
            "name": "second_channel",
            "is_public": True,
        },
    )
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config.url}/channels/create/v2",
        json={
            "token": token,
            "name": "private_channel",
            "is_public": False,
        },
    )
    requests.post(
        f"{config.url}/channel/join/v2",
        json={"token": new_token.json()["token"], "channel_id": 0},
    )
    requests.post(
        f"{config.url}/channel/join/v2",
        json={"token": new_token.json()["token"], "channel_id": 1},
    )
    # Creating a dm with both users
    timestamps.append(math.floor(time.time))
    requests.get(f"{config.url}/dm/create/v1", json={"token": token, "u_ids": 1})
    # Sending messages with the user
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config_url}/message/send/v1", 
        json={
            "token": token, 
            "channel_id": 0,
            "message": "Test Message"
            })
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config_url}/message/send/v1", 
        json={
            "token": token, 
            "channel_id": 0,
            "message": "Another Test Message"
            })
    timestamps.append(math.floor(time.time))
    requests.post(
        f"{config_url}/message/send/v1", 
        json={
            "token": token, 
            "channel_id": 0,
            "message": "A final test message"
    })
    response = requests.get(f"{config.url}/user/stats/v1", params={"token": token})
    assert response.status_code == OK
    assert response == {
        "channels_joined": [
            {"num_channels_joined": 3, "time_stamp": timestamps[2]},
            {"num_channels_joined": 2, "time_stamp": timestamps[1]},
            {"num_channels_joined": 1, "time_stamp": timestamps[0]},
            {"num_channels_joined": 0, "time_stamp": timestamp}],
        "dms_joined": [
            {"num_dms_joined": 1, "time_stamp": timestamps[3]},
            {"num_dms_joined": 0, "time_stamp": timestamp}],
        "messages_sent": [
            {"num_messages_sent": 3, "time_stamp": timestamps[6]},
            {"num_messages_sent": 2, "time_stamp": timestamps[5]},
            {"num_messages_sent": 1, "time_stamp": timestamps[4]},
            {"num_messages_sent": 0, "time_stamp": timestamp}],
        "involvement_rate": 1,
    }