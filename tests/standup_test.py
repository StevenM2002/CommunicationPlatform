
from src import config
from src.error import InputError, AccessError
import pytest
import requests
from datetime import timezone
import datetime
import time
OK = 200

@pytest.fixture
def setup_public():
    requests.delete(config.url + "clear/v1")
    response = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "jon.doe@gmail.com",
            "password": "rabbits",
            "name_first": "Jon",
            "name_last": "Doe",
        },
    )
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "don.joe@gmail.com",
            "password": "babbits",
            "name_first": "Don",
            "name_last": "Joe",
        },
    )
    user_id = r.json()["auth_user_id"]
    user_token = r.json()["token"]
    token = response.json()["token"]
    token_id = response.json()["auth_user_id"]
    # create a public channel
    response = requests.post(
        config.url + "channels/create/v2",
        json={"token": token, "name": "public_channel", "is_public": True},
    )
    channel_id = response.json()["channel_id"]
    return {
        "user_id": user_id,
        "channel_id": channel_id,
        "token_id": token_id,
        "token": token,
        "user_token": user_token,
    }

# standup active tests
def test_standup_active(setup_public):
    data = setup_public
    channel_id = data['channel_id']
    token = data['token']
    r = requests.get(config.url + 'standup/active/v1', \
        params={
            'token': token,
            'channel_id': channel_id
        },
    )
    assert r.status_code == OK
    assert not r.json()['is_active']
    assert r.json()['time_finish'] == None

def test_active_invalid_channel(setup_public):
    data = setup_public
    channel_id = data['channel_id'] + 1
    token = data['token']
    r = requests.get(config.url + 'standup/active/v1', \
        params={
            'token': token,
            'channel_id': channel_id
        },
    )
    assert (r.status_code == InputError.code)

def test_active_auth_not_member(setup_public):
    data = setup_public
    channel_id = data['channel_id']
    token = data['user_token']
    r = requests.get(config.url + 'standup/active/v1', \
        params={
            'token': token,
            'channel_id': channel_id
        },
    )
    assert r.status_code == AccessError.code

# standup start tests
def test_standup_start(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id']
    length = 300
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == OK
    assert round(r.json()['time_finish'], 1) == \
        round(datetime.datetime.now().replace(tzinfo=timezone.utc).timestamp() \
            + length, 1)
    r = requests.get(config.url + 'standup/active/v1', 
        params={
            'token': token,
            'channel_id': channel_id
        },
    )
    assert r.status_code == OK
    assert r.json()['is_active']


def test_start_invalid_channel(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id'] + 1
    length = 300
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == InputError.code

def test_start_auth_not_member(setup_public):
    data = setup_public
    token = data['user_token']
    channel_id = data['channel_id']
    length = 10
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == AccessError.code

def test_start_negative_length(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id']
    length = -300
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == InputError.code

def test_start_standup_already_running(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id']
    length = 10
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == OK
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length + 5
        },
    )
    assert r.status_code == InputError.code

# standup send tests
def test_standup_send(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id']
    length = 20
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == OK
    r = requests.post(config.url + 'standup/send/v1', 
        json={
            'token': token,
            'channel_id': channel_id,
            'message': "This is a test standup message"
        },
    )
    assert r.status_code == OK
    time.sleep(25)
    r = requests.get(config.url + 'channel/messages/v2', 
        params={
            "token": token,
            "channel_id": channel_id,
            "start": 0
        },
    )
    assert r.status_code == OK
    message = r.json()['messages'][0]['message']
    assert message == "jondoe: This is a test standup message" + "\n"
def test_send_invalid_channel(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id']
    length = 300
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == OK
    r = requests.post(config.url + 'standup/send/v1', 
        json={
            'token': token,
            'channel_id': channel_id + 1,
            'message': "This is a test standup message"
        },
    )
    assert r.status_code == InputError.code
    

def test_send_message_too_long(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id']
    length = 300
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == OK
    r = requests.post(config.url + 'standup/send/v1', 
        json={
            'token': token,
            'channel_id': channel_id,
            'message': "This is a test standup message that is over 1000 \
            characters but i'm not going to write out 1000 unique \
            characters so i will just keep looping this one for a while" + \
            "This is a test standup message that is over 1000 \
            characters but i'm not going to write out 1000 unique \
            characters so i will just keep looping this one for a while" + \
            "This is a test standup message that is over 1000 \
            characters but i'm not going to write out 1000 unique \
            characters so i will just keep looping this one for a while" + \
            "This is a test standup message that is over 1000 \
            characters but i'm not going to write out 1000 unique \
            characters so i will just keep looping this one for a while" + \
            "This is a test standup message that is over 1000 \
            characters but i'm not going to write out 1000 unique \
            characters so i will just keep looping this one for a while" + \
            "This is a test standup message that is over 1000 \
            characters but i'm not going to write out 1000 unique \
            characters so i will just keep looping this one for a while" + \
            "This is a test standup message that is over 1000 \
            characters but i'm not going to write out 1000 unique \
            characters so i will just keep looping this one for a while" + \
            "This is a test standup message that is over 1000 \
            characters but i'm not going to write out 1000 unique \
            characters so i will just keep looping this one for a while"
        },
    )
    assert r.status_code == InputError.code

def test_send_auth_not_member(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id']
    length = 300
    r = requests.post(config.url + 'standup/start/v1',
        json={
            'token': token,
            'channel_id': channel_id,
            'length': length
        },
    )
    assert r.status_code == OK
    r = requests.post(config.url + 'standup/send/v1', 
        json={
            'token': data['user_token'],
            'channel_id': channel_id,
            'message': "This is a test standup message"
        },
    )
    assert r.status_code == AccessError.code

def test_send_standup_not_running(setup_public):
    data = setup_public
    token = data['token']
    channel_id = data['channel_id']
    r = requests.post(config.url + 'standup/send/v1', 
        json={
            'token': token,
            'channel_id': channel_id,
            'message': "This is a test standup message"
        },
    )
    assert r.status_code == InputError.code