import pytest
from src.error import InputError, AccessError
import requests
import json
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
    assert response.status_code == 200
    r = requests.post(config.url + 'auth/register/v2', 
        json={
        "email": "don.joe@gmail.com", 
        "password": "babbits", 
        "name_first": "Don", 
        "name_last":"Joe"
        }
    )
    assert r.status_code == 200
    user_id = r.json()['auth_user_id']
    user_token = r.json()['token']
    token = response.json()['token']
    token_id = response.json()['auth_user_id']
    # decoy channel for coverage
    r = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': token, 'name': 'public_channel_bud', 'is_public': True
        }
    )
    assert r.status_code == 200
    # create a public channel
    response = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': token, 'name': 'public_channel', 'is_public': True
        }
    )
    assert response.status_code == 200
    channel_id = response.json()['channel_id']
    r = requests.post(config.url + 'channel/join/v2', 
        json= {
            'token': user_token, 
            'channel_id': channel_id
        }
    )
    assert r.status_code == 200
    return {'user_id': user_id, 'channel_id': channel_id, 'token_id': token_id,\
        'token': token, 'user_token': user_token}


def test_admin_user_remove(setup_public):
    data = setup_public
    token = data['token']
    u_id = data['user_id']
    user_token = data['user_token']
    token_id = data['token_id']
    channel_id = data['channel_id']
    r = requests.post(
        config.url + "auth/register/v2",
        json={
            "email": "gon.goe@dmail.com",
            "password": "barrits",
            "name_first": "Noj",
            "name_last": "Eod",
        },
    )
    throwaway = r.json()['auth_user_id']
    r = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': user_token, 'name': 'pub_channel', 'is_public': True
        }
    )
    assert r.status_code == 200
    c_id = r.json()['channel_id']
    r = requests.post(config.url + 'dm/create/v1', json=
        {
            'token': token,
            'u_ids': [u_id]
        }
    )
    assert r.status_code == 200
    dm_id = r.json()['dm_id']
    r = requests.post(config.url + 'dm/create/v1', json=
        {
            'token': user_token,
            'u_ids': [token_id]
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'dm/create/v1', json=
        {
            'token': token,
            'u_ids': [throwaway]
        }
    )
    r = requests.post(config.url + 'message/send/v1', json=
        {
            'token': token,
            'channel_id': data['channel_id'],
            'message': 'This is another test message'
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'message/send/v1', json=
        {
            'token': user_token,
            'channel_id': c_id,
            'message': 'This is a test message'
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'message/senddm/v1', json=
        {
            'token': user_token,
            'dm_id': dm_id,
            'message': 'This is yet another test message'
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'message/senddm/v1', json=
        {
            'token': token,
            'dm_id': dm_id,
            'message': 'This is another yet another test message'
        }
    )
    assert r.status_code == 200
    r = requests.delete(config.url + 'admin/user/remove/v1', 
        json= {
            'token': token,
            'u_id': u_id   
        }
    )
    assert r.status_code == 200
    r = requests.get(config.url + 'channel/details/v2', params= 
        {
            'token': token,
            'channel_id': channel_id
        }
    )
    assert r.status_code == 200
    members = r.json()['all_members']
    assert u_id not in members
    r = requests.get(config.url + 'users/all/v1', params=
        {
            'token': token
        }
    )
    assert r.status_code == 200
    users = r.json()['users']
    for user in users:
        assert user['u_id'] != u_id
    r = requests.get(config.url + 'user/profile/v1', params=
        {
            'token': token,
            'u_id': u_id
        }
    )
    assert r.status_code == 200
    user = r.json()['user']
    assert (user['name_first'] == 'Removed' and user['name_last'] == 'user')
    r = requests.get(config.url + 'dm/details/v1', json=
        {
            'token': token,
            'dm_id': dm_id
        }
    )
    assert r.status_code == 200
    members = r.json()['members']
    for member in members:
        assert member['u_id'] != u_id

def test_remove_invalid_user(setup_public):
    data = setup_public
    token = data['token']
    u_id = data['user_id'] + data['token_id'] + 1
    r = requests.delete(config.url + 'admin/user/remove/v1', 
        json= {
            'token': token,
            'u_id': u_id   
        }
    )
    assert r.status_code == InputError.code
def test_remove_only_globalowner(setup_public):
    data = setup_public
    token = data['token']
    u_id = data['token_id']
    r = requests.delete(config.url + 'admin/user/remove/v1', 
        json= {
            'token': token,
            'u_id': u_id   
        }
    )
    assert r.status_code == InputError.code

def test_remove_auth_not_globalowner(setup_public):
    data = setup_public
    token = data['user_token']
    u_id = data['user_id']
    r = requests.delete(config.url + 'admin/user/remove/v1', 
        json= {
            'token': token,
            'u_id': u_id   
        }
    )
    assert r.status_code == AccessError.code


def test_admin_userpermission_change(setup_public):
    data = setup_public
    token = data['token']
    u_id = data['user_id']
    user_token = data['user_token']
    r = requests.post(config.url + 'admin/userpermission/change/v1', json=
        {
            'token': token,
            'u_id': u_id,
            'permission_id': 2
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'admin/userpermission/change/v1', json=
        {
            'token': token,
            'u_id': u_id,
            'permission_id': 1
        }
    )
    r = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': token, 'name': 'public_channel_2', 'is_public': False
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'channel/join/v2', json=
        {
            'token': user_token,
            'channel_id': r.json()['channel_id']
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'admin/userpermission/change/v1', json=
        {
            'token': token,
            'u_id': u_id,
            'permission_id': 1
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'admin/userpermission/change/v1', json=
        {
            'token': token,
            'u_id': u_id,
            'permission_id': 2
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'channels/create/v2', 
        json={
            'token': token, 'name': 'public_channel_3', 'is_public': False
        }
    )
    assert r.status_code == 200
    r = requests.post(config.url + 'channel/join/v2', json=
        {
            'token': user_token,
            'channel_id': r.json()['channel_id']
        }
    )
    assert r.status_code == AccessError.code

def test_userpermission_invalid_user(setup_public):
    data = setup_public
    token = data['token']
    u_id = data['user_id'] + data['token_id'] + 1
    r = requests.post(config.url + 'admin/userpermission/change/v1', json=
        {
            'token': token,
            'u_id': u_id,
            'permission_id': 1
        }
    )
    assert r.status_code == InputError.code
def test_userpermission_only_globalowner_to_user(setup_public):
    data = setup_public
    token = data['token']
    u_id = data['token_id']
    r = requests.post(config.url + 'admin/userpermission/change/v1', json=
        {
            'token': token,
            'u_id': u_id,
            'permission_id': 2
        }
    )
    assert r.status_code == InputError.code

def test_userpermission_perm_id_invalid(setup_public):
    data = setup_public
    token = data['token']
    u_id = data['user_id']
    r = requests.post(config.url + 'admin/userpermission/change/v1', json=
        {
            'token': token,
            'u_id': u_id,
            'permission_id': 3
        }
    )
    assert r.status_code == InputError.code

def test_userpermission_auth_not_globalowner(setup_public):
    data = setup_public
    token = data['user_token']
    u_id = data['token_id']
    r = requests.post(config.url + 'admin/userpermission/change/v1', json=
        {
            'token': token,
            'u_id': u_id,
            'permission_id': 2
        }
    )
    assert r.status_code == AccessError.code