from src.data_store import data_store


def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {}


def channel_details_v1(auth_user_id, channel_id):
    """Finds a channel given an auth_user_id and a channel id, and returns
    the details of the channel

    Arguments:
        auth_user_id (integer) - unique id of user
        channel_id (integer) - unique id of channel

    Exceptions:
        InputError - Occurs when:
            - channel_id does not refer to a valid channel
        AccessError - Occurs when:
            - channel_id is valid and the authorised user is not a member
              of the channel

    Return Value:
        Returns {channel_name, owner_members, and all _members}"""

    # Importing the data_store
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # Checks whether the channel_id is used
    valid = any(True for channel in channels if channel["channel_id"] == channel_id)
    if not valid:
        raise InputError("Channel_id not found")

    # Checks whether auth_user_id is a member of the channel
    is_member = any(True for user in users if user["all_members"] == user)
    if not is_member:
        raise AccessError("User is not a member of the channel")

    # Finds the given channel, and saves the given data to a dictionary
    found_channel = [
        channel for channel in channels if channel["channel_id"] == channel_id
    ]

    printf(found_channel)
    return {
        "name": "Hayden",
        "owner_members": [
            {
                "u_id": 1,
                "email": "example@gmail.com",
                "name_first": "Hayden",
                "name_last": "Jacobs",
                "handle_str": "haydenjacobs",
            }
        ],
        "all_members": [
            {
                "u_id": 1,
                "email": "example@gmail.com",
                "name_first": "Hayden",
                "name_last": "Jacobs",
                "handle_str": "haydenjacobs",
            }
        ],
    }


def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        "messages": [
            {
                "message_id": 1,
                "u_id": 1,
                "message": "Hello world",
                "time_created": 1582426789,
            }
        ],
        "start": 0,
        "end": 50,
    }


def channel_join_v1(auth_user_id, channel_id):
    return {}
