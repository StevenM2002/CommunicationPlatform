from src.auth import extract_token
from datetime import timezone
import datetime
import time
import math
import threading
from src.data_store import data_store
from src.error import InputError, AccessError
def is_valid_channel(channels, channel_id):
    for channel in channels:
        if channel['channel_id'] == channel_id:
            return True
    return False
    
def auth_not_member(channels, channel_id, auth_user_id):
    for channel in channels:
        if channel['channel_id'] == channel_id:
            standup_channel = channel
    return auth_user_id not in standup_channel['all_members']

def end_standup(auth_user_id, channel, standup):
    data = data_store.get()
    message_id = data["max_ids"]["message"] + 1
    data["max_ids"]["message"] += 1
    message =  {
        "message": standup["message_queue"],
        "message_id": message_id,
        "time_created": math.floor(time.time()),
        "u_id": auth_user_id,
    }
    channel["messages"].insert(0, message)
    for standups in data["standups"]:
        if standups == standup:
            data["standups"].remove(standup)
        
    data_store.set(data)
def standup_start_v1(token, channel_id, length):
    store = data_store.get()
    auth_user_id = extract_token(token)['u_id']
    channels = store['channels']
    
    if not is_valid_channel(channels, channel_id):
        raise InputError("channel_id does not refer to a valid channel")
    
    if auth_not_member(channels, channel_id, auth_user_id):
        raise AccessError("channel_id is valid and the authorised user \
            is not a member of the channel")

    if (not length >= 0):
        raise InputError("length is a negative integer")

    if standup_active_v1(token, channel_id)['is_active']:
        raise InputError("an active standup is currently running \
            in the channel")

    for channel in channels:
        if channel["channel_id"] == channel_id:
            standup_channel = channel

    standups = store["standups"]
    dt = datetime.datetime.now()
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    timestamp += length
    new_standup = {
        "channel_id": channel_id,
        "time_finish": timestamp,
        "message_queue": ""
    }
    standups.append(new_standup)

    data_store.set(store)
    threading.Timer(length, end_standup, [auth_user_id, standup_channel, \
        new_standup]).start()
    return {"time_finish": timestamp}
def standup_active_v1(token, channel_id):
    store = data_store.get()
    channels = store["channels"]
    auth_user_id = extract_token(token)['u_id']
    
    if not is_valid_channel(channels, channel_id):
        raise InputError("channel_id does not refer to a valid channel")

    if auth_not_member(channels, channel_id, auth_user_id):
        raise AccessError("channel_id is valid and the authorised user \
            is not a member of the channel")
    
    for standup in store["standups"]:
        if (standup["channel_id"] == channel_id and standup["time_finish"] \
            > datetime.datetime.now().replace(tzinfo=timezone.utc).timestamp()):
            return {
                "is_active": True,
                "time_finish": standup["time_finish"]
            }
    return {
        "is_active": False, 
        "time_finish": None
    }
def standup_send_v1(token, channel_id, message):
    store = data_store.get()
    channels = store["channels"]
    auth_user_id = extract_token(token)['u_id']

    if not is_valid_channel(channels, channel_id):
        raise InputError("channel_id does not refer to a valid channel")

    if auth_not_member(channels, channel_id, auth_user_id):
        raise AccessError("channel_id is valid and the authorised user is \
            not a member of the channel")

    if not standup_active_v1(token, channel_id)["is_active"]:
        raise InputError("an active standup is not currently running in \
            the channel")

    if len(message) > 1000:
        raise InputError("length of message is over 1000 characters")
    for standups in store["standups"]:
        if standups["channel_id"] == channel_id:
            standup = standups
            break
    for users in store["users"]:
        if users["u_id"] == auth_user_id:
            name = users["handle_str"]
    standup["message_queue"] += f"{name}: {message}\n"
    data_store.set(store)
    return {}
    