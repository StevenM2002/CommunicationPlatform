from src.data_store import data_store
from src.error import InputError, AccessError


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

    # Finds the given channel, and saves the given data to a dictionary
    found_channel = [
        channel for channel in channels if channel["channel_id"] == channel_id
    ][0]

    # Checks whether auth_user_id is a member of the channel
    is_member = any(
        True for user in found_channel["all_members"] if user == auth_user_id
    )
    if not is_member:
        raise AccessError("User is not a member of the channel")

    # Loops through the users list, removing all passwords
    for user in users:
        user.pop("password")

    # Finds the user information for each owner of the channel
    for i in range(len(found_channel["owner_members"])):
        user_id = found_channel["owner_members"][i]
        print("owners")
        print([user for user in users if user["u_id"] == user_id])
        found_channel["owner_members"][i] = [
            user for user in users if user["u_id"] == user_id
        ][0]

    # Finds the user information for each member of the channel
    print("All members auth_user_ids")
    print(found_channel["all_members"])
    for i in range(len(found_channel["all_members"])):
        user_id = found_channel["all_members"][i]
        print("members")
        print([user for user in users if user["u_id"] == user_id])
        found_channel["all_members"][i] = [
            user for user in users if user["u_id"] == user_id
        ][0]

    found_channel.pop("channel_id")
    found_channel.pop("is_public")
    print(f"found_channel: {found_channel}")

    return found_channel


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
