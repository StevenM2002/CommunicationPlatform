"""Interfaces that operate on channels

Contains functions for inviting users to a channel, getting details or messages
from a channel. Each of these functions are decorated with validate_auth_id to
ensure that auth_user_id is valid before running code inside the functions.

    Typical usage example:

    from src.auth import auth_login_v1
    from src.channel import channel_invite_v1

    user_id = auth_login_v1("matthew@gmail.com", "strongpassword")
    channel_id = 420

    channel_invite_v1(user_id, channel_id, user_id)
"""
from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import validate_auth_id, first

EXCLUDE_LIST = ["password", "session_ids"]


@validate_auth_id
def channel_invite_v1(auth_user_id, channel_id, u_id):
    """Invites a user with ID u_id to join a channel with ID channel_id.

    Once invited, the user is added to the channel immediately. In both public
    and private channels, all members are able to invite users.

    Arguments:
        auth_user_id (int) - id of user inviting
        channel_id (int) - id of given channel
        u_id (int) - id of user being invited

    Exceptions:
        InputError - Occurs when:
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is already a member of the channel
        AccessError - Occurs when:
            - auth_user_id does not belong to a user
            - channel_id is valid and the authorised user is not a member of
            the channel

    Return Value:
        Returns {} if invite is successful
    """
    store = data_store.get()
    channel_list = store["channels"]
    user_list = store["users"]

    # loop through channels to verify the channel_id belongs to an actual
    # channel if the channel is found, save it to variable channel
    valid_channel = False
    for each_channel in channel_list:
        if each_channel["channel_id"] == channel_id:
            valid_channel = True
            channel = each_channel
    if not valid_channel:
        raise InputError("channel_id does not refer to a valid channel")

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
        raise InputError("u_id refers to a user who is already a member of the channel")
    # loop through user_list to check u_id corresponds to an actual user
    valid_user = any(True for each_user in user_list if each_user["u_id"] == u_id)
    if not valid_user:
        raise InputError("u_id does not refer to a valid user")

    # if no errors were raised, add u_id to the list of members of the channel
    channel["all_members"].append(u_id)
    return {}


@validate_auth_id
def channel_details_v1(auth_user_id, channel_id):
    """Get name, visibility, owners and members of a channel.

    Arguments:
        auth_user_id (int) - id of authorised user
        channel_id (int) - id of channel to get details of

    Exceptions:
        InputError - Occurs when:
            - channel_id does not refer to a valid channel
        AccessError - Occurs when:
            - auth_user_id does not belong to a user
            - channel_id is valid and the authorised user is not a member of
            the channel

    Return Value:
        Returns {channel_name, is_public, owner_members, and all_members}
    """
    store = data_store.get()
    users = store["users"]
    channels = store["channels"]

    # checks whether the channel_id is used
    valid = any(True for channel in channels if channel["channel_id"] == channel_id)
    if not valid:
        raise InputError("channel_id not found")

    # finds the given channel, and saves the given data to a dictionary
    found_channel = [
        channel for channel in channels if channel["channel_id"] == channel_id
    ][0]

    # checks whether auth_user_id is a member of the channel
    is_member = any(
        True for user in found_channel["all_members"] if user == auth_user_id
    )
    if not is_member:
        raise AccessError("user is not a member of the channel")

    # loops through the tuple containing owner_members and all_members, finding
    # the user from the user_id and adding it to the corresponding list
    for member_key in ("owner_members", "all_members"):
        for i, user_id in enumerate(found_channel[member_key]):
            member_user = [user for user in users if user["u_id"] == user_id][0]
            found_channel[member_key][i] = {
                key: value
                for key, value in member_user.items()
                if key not in EXCLUDE_LIST
            }

    # return found_channel excluding for channel_id and messages keys
    return {
        key: value
        for key, value in found_channel.items()
        if key not in ("channel_id", "messages")
    }


@validate_auth_id
def channel_messages_v1(auth_user_id, channel_id, start):
    """Get the messages from a channels.

    Arguments:
        auth_user_id (integer) - id of user requesting messages
        channel_id (integer) - id of channel to get messages from
        start (integer) - index of first message to start from

    Exceptions:
        AccessError - Occurs when:
            - auth_user_id does not belong to a user
            - channel_id is valid and the authorised user is not a member of
            the channel
        InputError - Occurs when:
            - channel_id does not refer to a valid channel
            - start is greater than the total number of messages in the channel

    Returns:
        Returns {messages, start, end}
    """
    # channel is set to the channel that matches the given channel_id if none
    # match then it is set to an empty dictionary
    channels = data_store.get()["channels"]
    channel = first(lambda c: c["channel_id"] == channel_id, channels, {})
    if not channel:
        raise InputError("no channel matching channel id")
    if not auth_user_id in channel["all_members"]:
        raise AccessError("user is not a member of this channel")
    messages = len(channel["messages"]) - 1
    if start > messages:
        raise InputError("start message id is greater than latest message id")

    # end is set to -1 if the most recent message has been returned
    return {
        "messages": channel["messages"][start : start + 50],
        "start": start,
        "end": start + 50 if start + 50 < messages else -1,
    }


@validate_auth_id
def channel_join_v1(auth_user_id, channel_id):
    """Add a user to a channel.

    Arguments:
        auth_user_id (int) - id of user joining the channel
        channel_id (int) - id of channel to join

    Exceptions:
        InputError - Occurs when:
            - channel_id does not refer to a valid channel
            - the authorised user is already a member of the channel
        AccessError - Occurs when:
            - auth_user_id does not belong to a user
            - channel_id refers to a channel that is private and the authorised
            user is not already a channel member and is not a global owner

    Return Value:
        Returns {} if join is successful
    """
    store = data_store.get()

    # find first channel matching channel_id if none found set to empty dict
    channel = first(lambda c: c["channel_id"] == channel_id, store["channels"], {})
    if not channel:
        raise InputError("channel_id does not refer to a valid channel")

    # checks if the user is already in the given channel
    for member in channel["all_members"]:
        if member == auth_user_id:
            raise InputError("user is already a member of the channel")
    # makes sure the channel is not private
    if not channel["is_public"] and auth_user_id not in store["global_owners"]:
        raise AccessError(
            "channel_id refers to a channel that is private and the \
            authorised user is not a global owner"
        )

    # adds the user to the channel members list
    channel["all_members"].append(auth_user_id)
    return {}
