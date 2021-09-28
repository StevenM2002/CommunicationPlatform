from src.data_store import data_store
from src.error import AccessError, InputError


def channel_invite_v1(auth_user_id, channel_id, u_id):
    """
    Invites a user with ID u_id to join a channel with ID channel_id. Once
    invited, the user is added to the channel immediately. In both public and
    private channels, all members are able to invite users.

    Arguments:
        auth_user_id (integer)    - id of authorised user
        channel_id (integer)    - id of given channel
        u_id (integer)    - id of user being invited

    Exceptions:
        InputError  - Occurs when:
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is already a member of the channel
        AccessError - Occurs when:
            - channel_id is valid and the authorised user is not a member 
            of the channel

    Return Value:
        Returns {} if invite is successful
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
    if not valid_channel:
        raise InputError("channel_id does not refer to a valid channel")

    # loop through user_list to check u_id corresponds to an actual user
    valid_user = any(True for each_user in user_list if each_user["u_id"] == \
    u_id)
    if not valid_user:
        raise InputError("u_id does not refer to a valid user")

    # loop through members of channel to make sure auth_user_id is actually
    # a member of the channel, and also that u_id is not already in the channel
    valid_member = False
    uid_in_channel = False
    for users in channel["all_members"]:
        if users == auth_user_id:
            valid_member = True
        if users == u_id:
            uid_in_channel = True
    if not valid_member:
        raise AccessError("the authorised user is not a member of the channel")
    if uid_in_channel:
        raise InputError(
            "u_id refers to a user who is already a member of \
            the channel"
        )

    # if no errors were raised, add u_id to the list of members of the channel
    channel["all_members"].append(u_id)
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
    """Given a channel_id of a channel that the authorised user can join,
    adds them to that channel.

    Arguments:
        auth_user_id (integer)    - id of user joining the channel
        channel_id (integer)    - id of given channel

    Exceptions:
        InputError  - Occurs when:
            - channel_id does not refer to a valid channel
            - the authorised user is already a member of the channel
        AccessError - Occurs when:
            - channel_id refers to a channel that is private and the authorised 
            user is not already a channel member and is not a global owner

    Return Value:
        Returns {} if join is successful
    """

    store = data_store.get()
    # find user corresponding to the id passed into the function, save this user
    # to a dictionary
    for users in store["users"]:
        if users["u_id"] == auth_user_id:
            to_add = users

    # determine if c_id represents an actual channel, and if so saves this
    # channel to a dictionary
    is_valid_channel = False
    for channels in store["channels"]:
        if channels["channel_id"] == channel_id:
            to_add_to = channels
            is_valid_channel = True
    if not is_valid_channel:
        raise InputError("channel_id does not refer to a valid channel")

    # checks if the user to add is already in the given channel
    for each_user in to_add_to["all_members"]:
        if each_user == auth_user_id:
            raise InputError(
                "the authorised user is already a member of the \
                channel"
            )
    # makes sure the channel is not private
    if not to_add_to["is_public"] and to_add["u_id"] != \
    channels["owner_members"]:
        raise AccessError(
            "channel_id refers to a channel that is private and \
            the authorised user is not a global owner"
        )

    # adds the user to the channel members list
    to_add_to["all_members"].append(auth_user_id)
    return {}
