"""Tests for functions from src/channel.py"""
import pytest
import requests
import json
from src.error import InputError, AccessError
from src.other import clear_v1
from src.data_store import data_store
from src import config 
import requests 

@pytest.fixture
def setup_public():
    requests.delete(config.url + "clear/v1")
    response = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "jon.doe@gmail.com", 
        "password": "rabbits", 
        "name_first": "Jon", 
        "name_last":"Doe"
        }
    )
    r = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "don.joe@gmail.com", 
        "password": "babbits", 
        "name_first": "Don", 
        "name_last":"Joe"
        }
    )
    user_id = r.json()['auth_user_id']
    user_token = r.json()['token']
    token = response.json()['token']
    token_id = response.json()['auth_user_id']
    # create a public channel
    response = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': token, 'name': 'public_channel', 'is_public': True
        }
    )
    channel_id = response.json()['channel_id']
    return {'user_id': user_id, 'channel_id': channel_id, 'token_id': token_id,\
        'token': token, 'user_token': user_token}
@pytest.fixture
def setup_private():
    requests.delete(config.url + "clear/v1")
    resp = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "gon.goe@dmail.com", 
        "password": "barrits", 
        "name_first": "Noj", 
        "name_last":"Eod"
        }
    )
    global_token = resp.json()['token']
    response = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "jon.doe@gmail.com", 
        "password": "rabbits", 
        "name_first": "Jon", 
        "name_last":"Doe"
        }
    )
    r = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "don.joe@gmail.com", 
        "password": "babbits", 
        "name_first": "Don", 
        "name_last":"Joe"
        }
    )
    user_id = r.json()['auth_user_id']
    user_token = r.json()['token']
    token = response.json()['token']
    token_id = response.json()['auth_user_id']
    # create a private channel
    response = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': token, 'name': 'public_channel', 'is_public': False
        }
    )
    channel_id = response.json()['channel_id']
    return {'user_id': user_id, 'channel_id': channel_id, 'token_id': token_id,\
        'user_token': user_token, 'token': token, 'global_token': global_token}
# channel invite tests
def test_channel_invite(setup_public):
    data = setup_public
    u_id = data['user_id']
    channel_id = data['channel_id']
    token = data['token']
    user_token = data['user_token']
    response = requests.post(config.url + 'channel/invite/v2', 
        json = {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == 200
    response = requests.get(config.url + 'channel/details/v2', 
        json= {
            'token': user_token,
            'channel_id': channel_id
        }
  
    )
    assert response.status_code == 200
def test_invite_invalid_channel(setup_public):
    data = setup_public
    u_id = data['user_id']
    channel_id = data['channel_id'] + 1
    token = data['token']
    response = requests.post(config.url + 'channel/invite/v2', 
        json= {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == InputError.code

def test_invite_invalid_user(setup_public):
    data = setup_public
    u_id = data['user_id'] + data['token_id'] + 1
    channel_id = data['channel_id']
    token = data['token']
    response = requests.post(config.url + 'channel/invite/v2', 
        json= {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == InputError.code

def test_invite_auth_not_member(setup_public):
    data = setup_public
    u_id = data['user_id']
    channel_id = data['channel_id']
    r = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "lbandas@gmail.com", 
        "password": "password", 
        "name_first": "Lewis", 
        "name_last":"Bandas"
        }
    )
    assert r.status_code == 200
    fake_token = r.json()['token']
    response = requests.post(config.url + 'channel/invite/v2', 
        json= {
            'token': fake_token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == AccessError.code


def test_invite_already_member(setup_public):
    data = setup_public
    u_id = data['user_id']
    channel_id = data['channel_id']
    token = data['token']
    requests.post(config.url + 'channel/invite/v2', 
        json = {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    response = requests.post(config.url + 'channel/invite/v2', 
        json = {
            'token': token,
            'channel_id': channel_id,
            'u_id': u_id
        }
    )
    assert response.status_code == InputError.code

# channel join tests
def test_channel_join(setup_public):
    data = setup_public
    token = data['user_token']
    channel_id = data['channel_id']
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == 200
    response = requests.get(config.url + 'channel/details/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == 200

def test_join_invalid_channel(setup_public):
    data = setup_public
    token = data['user_token']
    channel_id = data['channel_id'] + 1
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == InputError.code



def test_join_already_member(setup_public):
    data = setup_public
    token = data['user_token']
    channel_id = data['channel_id']
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == InputError.code

def test_join_priv_channel(setup_private):
    data = setup_private
    fake_token = data['user_token']
    channel_id = data['channel_id']
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': fake_token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == AccessError.code



def test_join_global_owner(setup_private):
    data = setup_private
    global_token = data['global_token']
    channel_id = data['channel_id']
    response = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': global_token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == 200
    response = requests.get(config.url + 'channel/details/v2', 
        json= {
            'token': global_token,
            'channel_id': channel_id
        }
    )
    assert response.status_code == 200
