"""Interfaces for managaing channels

Contains functions for listing channels public or private and creating a new
channel. Each of these functions are decorated with validate_auth_id to ensure
that auth_user_id is valid before running code inside the functions.
"""
from src.data_store import data_store
from src.error import InputError
from src.other import validate_auth_id


@validate_auth_id
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


@validate_auth_id
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


@validate_auth_id
def channels_create_v2(auth_user_id, name, is_public):
    """Create a new channel where auth_user_id is the owner.

    Arguments:
        auth_user_id (int) - unique id of user
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

    # checks for if the name is valid
    if len(name) < 1 or len(name) > 20:
        raise InputError("invalid Name")

    # sets channel_id as the next highest number in the channel list
    if len(channels) > 0:
        channel_id = max(channels, key=lambda c: c["channel_id"])["channel_id"] + 1
    else:
        channel_id = 0

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

    # update data store with changes
    data_store.set(store)
    return {
        "channel_id": channel_id,
    }
