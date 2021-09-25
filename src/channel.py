from src.data_store import data_store
from src.error import AccessError, InputError


def channel_invite_v1(auth_user_id, channel_id, u_id):
    """
    Invites a user with ID u_id to join a channel with ID channel_id. Once
    invited, the user is added to the channel immediately. In both public and
    private channels, all members are able to invite users.
    """
    store = data_store.get()
    channel_list = store["channels"]
    user_list = store["users"]

    # loop through channels to verify the channel_id belongs to an actual channel
    # if the channel is found, save it to variable "channel"
    valid_channel = False
    for each_channel in channel_list:
        if each_channel["channel_id"] == channel_id:
            valid_channel = True
            channel = each_channel
    if valid_channel == False:
        raise InputError("channel_id does not refer to a valid channel")

    # loop through user_list to check u_id corresponds to an actual user
    valid_user = False
    for each_user in user_list:
        if each_user["u_id"] == u_id:
            valid_user = True
    if valid_user == False:
        raise InputError("u_id does not refer to a valid user")

    # loop through members of channel to make sure auth_user_id is actually
    # a member of the channel, and also that u_id is not already in the channel
    valid_member = False
    uid_in_channel = False
    for users in channel["members"]:
        if users == auth_user_id:
            valid_member = True
        if users == u_id:
            uid_in_channel = True
    if valid_member == False:
        raise AccessError("the authorised user is not a member of the channel")
    if uid_in_channel == True:
        raise InputError(
            "u_id refers to a user who is already a member of \
            the channel"
        )

    # if no errors were raised, add u_id to the list of members of the channel
    channel["members"].append(u_id)
    return {}


def channel_details_v1(auth_user_id, channel_id):
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
