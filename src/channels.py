from src.data_store import data_store
from src.error import InputError, AccessError


def channels_list_v1(auth_user_id):
    return {
        "channels": [
            {
                "channel_id": 1,
                "name": "My Channel",
            }
        ],
    }


def channels_listall_v1(auth_user_id):
    return {
        "channels": [
            {
                "channel_id": 1,
                "name": "My Channel",
            }
        ],
    }


def channels_create_v1(auth_user_id, name, is_public):
    """Creates a new channel in the data_store when given an auth_user_id,
    name, and is_public identifier, returning the channel_id.

    Arguments:
        auth_user_id (integer) - unique id of user
        name (string) - name of user
        is_public (boolean) - whether the given channel is to be public or private

    Exceptions:
        InputError - Occurs when:
            - name is less than 1 character in length, or longer than 20 characters
        AccessError - Occurs when:
            - the input auth_user_id does not belong to any user in the data store

    Return Value:
        Returns {channel_id} upon succesful creation of channel"""

    # Retrieves the data store, and the channel dictionary
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # Determines if the auth_user_id is valid by checking for it in users
    valid = any(True for user in users if user["u_id"] == auth_user_id)

    if not valid:
        raise AccessError("Invalid user_id")

    # Checks for if the name is valid
    if len(name) < 1 or len(name) > 20:
        raise InputError("Invalid Name")

    # Sets channel_id as the next highest number in the channel list
    channel_id = (
        max(channels, key=lambda x: x["channel_id"])["channel_id"] + 1
        if len(channels) > 0
        else 0
    )

    channels.append(
        {
            "channel_id": channel_id,
            "name": name,
            "owner": auth_user_id,
            "members": [auth_user_id],
            "is_public": is_public,
        }
    )

    # Sets the data store
    data_store.set(store)
    return {
        "channel_id": channel_id,
    }
