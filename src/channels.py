"""Interfaces for managing channels

Contains functions for listing channels public or private and creating a new
channel. Each of these functions are decorated with validate_auth_id to ensure
that auth_user_id is valid before running code inside the functions.
"""
import math
import time
from src.data_store import data_store
from src.error import InputError
from src.auth import extract_token


def channels_list_v1(auth_user_id):
    """List all public channels.

    Giving ids and names of channels.

    Arguments:
        auth_user_id (int) - id of a user who is registered

    Exceptions:
        AccessError - Occurs when:
            - auth_user_id does not belong to a user

    Return Value:
        Returns {"channels": [{"channel_id": channel_id, "name": channel_name}]}
    """
    store = data_store.get()
    # iterate through channels if auth_user_id is a member of the channel add
    # channel to the return value
    channels = []
    for channel in store["channels"]:
        chan_info = {"channel_id": channel["channel_id"], "name": channel["name"]}
        for members in channel["all_members"]:
            if members == auth_user_id:
                channels.append(chan_info)

    return {"channels": channels}


def channels_listall_v1(auth_user_id):  # pylint: disable=unused-argument
    """List all public and private channels.

    Giving ids and names of channels.

    Arguments:
        auth_user_id (int) - a registered id of a user

    Exceptions:
        AccessError - Occurs when:
            - auth_user_id does not belong to a user

    Return Value:
        Returns {"channels": [{"channel_id": channel_id, "name": channel_name}]}
    """
    store = data_store.get()
    # get all channels including private channels
    channels = [
        {"channel_id": channel["channel_id"], "name": channel["name"]}
        for channel in store["channels"]
    ]
    return {"channels": channels}


def channels_create_v2(token, name, is_public):
    """Create a new channel where auth_user_id is the owner.

    Arguments:
        token (str) - unique token of session
        name (str) - name of user
        is_public (bool) - whether channel is public or private

    Exceptions:
        InputError - Occurs when:
            - name is less than 1 character or longer than 20 characters
        AccessError - Occurs when:
            - auth_user_id does not belong to a user in the data store

    Return Value:
        Returns {channel_id} upon succesful creation of channel"""
    # retrieves the data store, and the channel dictionary
    store = data_store.get()
    channels = store["channels"]
    users = store["users"]
    workspace = store["workspace_stats"]

    # Checks if the given token is valid
    u_information = extract_token(token)
    auth_user_id = u_information["u_id"]

    # checks for if the name is valid
    if len(name) < 1 or len(name) > 20:
        raise InputError(description="invalid Name")

    # sets channel_id as the next highest number in the channel list
    store["max_ids"]["channel"] += 1
    data_store.set(store)
    channel_id = store["max_ids"]["channel"]

    channels.append(
        {
            "channel_id": channel_id,
            "name": name,
            "owner_members": [auth_user_id],
            "all_members": [auth_user_id],
            "is_public": is_public,
            "messages": [],
        }
    )

    # Incrementing the workspace stats for the user
    increment_workspace_channels()

    # Updating the user stats for the owner
    incremement_user_channels(auth_user_id)

    # update data store with changes
    data_store.set(store)
    return {
        "channel_id": channel_id,
    }


def channels_list_v2(token):
    """
    This function provides a list of channel information given a token

    Arguments:
        token, token which is a jwt

    Exceptions:
        InputError  - NA
        AccessError - Occurs when the token is incorrect

    Return Value:
        Returns channels_list_v1 return which is of form {"channels": []}

    """
    payload = extract_token(token)
    return channels_list_v1(payload["u_id"])


def channels_listall_v2(token):
    """
    Given a valid token, give a list of all channels

    Arguments:
        token, is a jwt

    Exceptions:
        InputError  - NA
        AccessError - Occurs when there is an invalid token

    Return Value:
         Returns channels_listall_v1 return which is of form {"channels": []}
    """
    payload = extract_token(token)
    return channels_listall_v1(payload["u_id"])


def increment_workspace_channels():
    # Fetching the data store
    store = data_store.get()
    workspace = store["workspace_stats"]

    # Creating a timestamp and incrementing the workspace stats
    timestamp = math.floor(time.time())
    num_channels = workspace["channels_exist"][-1]["num_channels_exist"]
    workspace["channels_exist"].append(
        {"num_channels_exist": num_channels + 1, "time_stamp": timestamp}
    )


def incremement_user_channels(auth_user_id):
    # Fetching the data store
    users = data_store.get()["users"]

    # Finding the given user in the data store
    found_user = [user for user in users if user["u_id"] == auth_user_id][0]
    user_stats = found_user["user_stats"]

    # Creating a timestamp and saving the user stats
    timestamp = math.floor(time.time())

    # Incrementing channels_joined stat
    channels_joined_prev = user_stats["channels_joined"][-1]["num_channels_joined"]
    user_stats["channels_joined"].append(
        {"num_channels_joined": channels_joined_prev + 1, "time_stamp": timestamp}
    )
