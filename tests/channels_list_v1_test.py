import pytest
from src.channels import channels_create_v1
from src.other import clear_v1
from src.channel import channel_join_v1
'''
channels_list_v1
Provide a list of all channels 
(and their associated details) that the authorised user is part of.

Parameters:
{ auth_user_id }
integer

Return:
{ channels }
List of dictionaries, where each dictionary contains types { channel_id, name }
'''
'''
List both private and public channels
'''

def test_one_channel_public():
	clear_v1()
	chan_id1 = channels_create_v1(1, "one_channel", True)
	assert channels_list_v1(1) == [{"channel_id": chan_id1, "name": "one_channel"}]

def test_one_channel_private():
	clear_v1()
	chan_id1 = channels_create_v1(1, "one_channel", False)
	assert channels_list_v1(1) == [{"channel_id": chan_id1, "name": "one_channel"}]

def test_two_channels():
	clear_v1()
	chan_id1 = channels_create_v1(1, "first_channel", True)
	chan_id2 = channels_create_v1(1, "second_channel", False)
	assert channels_list_v1(1) == [
		{"channel_id": chan_id1, "name": "first_channel"}, 
		{"channel_id": chan_id2, "name": "second_channel"}
	]

def test_not_admin():
	clear_v1()
	chan_id1 = channels_create_v1(1, "first_channel", True)
	channels_join_v1(2, chan_id)
	assert channels_list_v1(2) == [
		{"channel_id": chan_id1, "name": "first_channel"}
	]

def test_not_in_channels():
	clear_v1()
	assert channels_list_v1(1) == None
	channels_create_v1(2, "first_channel", True)
	assert channels_list_v1(1) == None
	channels_create_v1(3, "second_channel", False)
	assert channels_list_v1(1) == None
	channels_create_v1(2, "third_channel", True)
	assert channels_list_v1(1) == None

def test_same_channel_name():
	clear_v1()
	chan_id1 = channels_create_v1(1, "first_channel", True)
	chan_id2 = channels_create_v1(1, "first_channel", False)
	assert channels_list_v1(1) = [
		{"channel_id": chan_id1, "name": "first_channel"}, 
		{"channel_id": chan_id2, "name": "first_channel"}
	]

def test_mixed_channels():
	clear_v1()
	chan_id1 = channels_create_v1(1, "first_channel", True)
	chan_id2 = channels_create_v1(1, "second_channel", False)
	chan_id3 = channels_create_v1(2, "second_channel", True)
	channels_join_v1(1, chan_id3)
	channels_create_v1(3, "fourth_channel", False)
	channels_create_v1(4, "fifth_channel", True)
	assert channels_list_v1(1) == [
		{"channel_id": chan_id1, "name": "first_channel"}, 
		{"channel_id": chan_id2, "name": "second_channel"}
		{"channel_id": chan_id3, "name": "second_channel"}
	]









