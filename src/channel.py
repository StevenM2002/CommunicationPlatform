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
from copy import deepcopy
import math
import time

from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import first
from src.auth import extract_token
from src import notifications


EXCLUDE_LIST = ["password", "session_ids", "channel_id", "messages", "user_stats"]


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

    # updating the user stats for the owner
    timestamp = math.floor(time.time())
    found_user = [user for user in user_list if user["u_id"] == u_id][0]
    user_stats = found_user["user_stats"]
    channels_joined_prev = user_stats["channels_joined"][-1]["num_channels_joined"]
    user_stats["channels_joined"].append(
        {"num_channels_joined": channels_joined_prev + 1, "time_stamp": timestamp}
    )

    data_store.set(store)
    notifications.add_added_to_a_channel_or_dm_to_notif(auth_user_id, u_id, channel_id, -1)
    return {}


def channel_details_v2(token, channel_id):
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
    u_information = extract_token(token)
    auth_user_id = int(u_information["u_id"])
    # Forces channel_id to be an integer
    channel_id = int(channel_id)

    channel = first(lambda c: c["channel_id"] == channel_id, channels, {})
    if not channel:
        raise InputError(description="channel_id not found")

    # checks whether auth_user_id is a member of the channel
    is_member = any(True for user in channel["all_members"] if user == auth_user_id)
    if not is_member:
        raise AccessError(description="user is not a member of the channel")

    # loops through the tuple containing owner_members and all_members, finding
    # the user from the user_id and adding it to the corresponding list
    channel_details = {
        key: value
        for key, value in deepcopy(channel).items()
        if key not in EXCLUDE_LIST
    }
    for member_key in ("owner_members", "all_members"):
        for i, user_id in enumerate(channel[member_key]):
            user_details = first(lambda u: u["u_id"] == user_id, users, {})
            channel_details[member_key][i] = {
                key: value
                for key, value in user_details.items()
                if key not in EXCLUDE_LIST
            }

    return channel_details


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
    users = store["users"]

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

    # updating the user stats for the owner
    timestamp = math.floor(time.time())
    found_user = [user for user in users if user["u_id"] == auth_user_id][0]
    user_stats = found_user["user_stats"]
    channels_joined_prev = user_stats["channels_joined"][-1]["num_channels_joined"]
    user_stats["channels_joined"].append(
        {"num_channels_joined": channels_joined_prev + 1, "time_stamp": timestamp}
    )

    data_store.set(store)
    return {}


def channel_addowner_v1(token, channel_id, u_id):
    """Adds owner to a channel

    Arguments:
        token (str) is a jwt, contains info on person accessing
        channel_id (int) is an int which specifies a specific channel
        u_id (int) is an int which specifies a specific user

    Exceptions:
        InputError  - Occurs when:
            u_id is not valid
            u_id is already in channel
            channel_id is not valid
            u_id is already owner
        AccessError - Occurs when:
            auth_user_id from token does not have owner perms
            token is invalid

    Return Value:
        returns {}
    """
    store = data_store.get()
    payload = extract_token(token)

    is_global_owner = False
    if payload["u_id"] in store["global_owners"]:
        is_global_owner = True
    all_u_ids = [users["u_id"] for users in store["users"]]
    all_chan_ids = [chans["channel_id"] for chans in store["channels"]]
    which_channel = None
    # Check for access errs
    for channels in store["channels"]:
        if channel_id == channels["channel_id"]:
            if (payload["u_id"] in channels["owner_members"]) or (
                payload["u_id"] in channels["all_members"] and is_global_owner
            ):
                which_channel = channels["owner_members"]
            else:
                raise AccessError("does not have owner perms")
    # Check for input errs
    if u_id not in all_u_ids:
        raise InputError("u_id not valid")
    if channel_id not in all_chan_ids:
        raise InputError("channel_id not valid")
    for channel in store["channels"]:
        if channel["channel_id"] == channel_id:
            if u_id not in channel["all_members"]:
                raise InputError("u_id not in channel")
            if u_id in channel["owner_members"]:
                raise InputError("u_id already owner")

    which_channel.append(u_id)
    data_store.set(store)
    return {}


def channel_removeowner_v1(token, channel_id, u_id):
    """This function removes the owner of a channel.

    Arguments:
        token, is a jwt, contains info on person accessing
        channel_id, is an int which specifies a specific channel
        u_id, is an int which specifies a specific user

    Exceptions:
        InputError  - Occurs when:
            u_id is not a valid user
            u_id is not an owner
            u_id is the only owner
            channel_id is not valid
        AccessError - Occurs when ...
            authorised user from token does not have owner perms
    Return Value:
        Returns {}
    """
    store = data_store.get()
    payload = extract_token(token)
    is_global_owner = False
    if payload["u_id"] in store["global_owners"]:
        is_global_owner = True
    all_u_ids = [users["u_id"] for users in store["users"]]
    all_chan_ids = [chans["channel_id"] for chans in store["channels"]]
    # Check for access errs
    for channels in store["channels"]:
        if channel_id == channels["channel_id"]:
            if (payload["u_id"] in channels["owner_members"]) or (
                payload["u_id"] in channels["all_members"] and is_global_owner
            ):
                which_channel = channels["owner_members"]
            else:
                raise AccessError("does not have owner perms")
    # Check for input errs
    if u_id not in all_u_ids:
        raise InputError("u_id not valid")
    if channel_id not in all_chan_ids:
        raise InputError("channel_id not valid")
    for channel in store["channels"]:
        if channel["channel_id"] == channel_id:
            if u_id not in channel["all_members"]:
                raise InputError("u_id not in channel")
            if u_id not in channel["owner_members"]:
                raise InputError("u_id not an owner")
            if len(channel["owner_members"]) == 1:
                raise InputError("cannot remove only channel owner")

    which_channel.remove(u_id)
    data_store.set(store)
    return {}


def channel_leave_v1(token, channel_id):
    """This function removes the owner of a channel

    Arguments:
        token, is a jwt, contains info on person accessing
        channel_id, is an int which specifies a specific channel

    Exceptions:
        InputError  - Occurs when:
            channel_id is not valid
        AccessError - Occurs when ...
            authorised user from token is not a member of the channel

    Return Value:
        Returns {}
    """
    store = data_store.get()
    payload = extract_token(token)
    # Check input err
    all_chan_ids = [chans["channel_id"] for chans in store["channels"]]
    if channel_id not in all_chan_ids:
        raise InputError("channel_id not valid")
    # Check access err and if all good, remove
    for channels in store["channels"]:
        if channel_id == channels["channel_id"]:
            if payload["u_id"] not in channels["all_members"]:
                raise AccessError("user not member in channel")
            else:
                channels["all_members"].remove(payload["u_id"])
                try:
                    channels["owner_members"].remove(payload["u_id"])
                except ValueError:
                    pass

    # updating the user stats for the owner
    timestamp = math.floor(time.time())
    found_user = [user for user in store["users"] if user["u_id"] == payload["u_id"]][0]
    user_stats = found_user["user_stats"]
    channels_joined_prev = user_stats["channels_joined"][-1]["num_channels_joined"]
    user_stats["channels_joined"].append(
        {"num_channels_joined": channels_joined_prev - 1, "time_stamp": timestamp}
    )

    return {}


def channel_invite_v2(token, channel_id, u_id):
    """Invite a user with u_id to a channel with channel_id.

    Arguments:
        token (str) - is a jwt, contains info on person accessing
        channel_id (int) - id of given channel
        u_id (int) - id of user being invited

    Exceptions:
        InputError when any of:
            - channel_id does not refer to a valid channel
            - u_id does not refer to a valid user
            - u_id refers to a user who is already a member of the
              channel

        AccessError when:
            - channel_id is valid and the authorised user is not a
              member of the channel

    Return Value:
        Returns {}
    """
    auth_id = extract_token(token)["u_id"]
    return channel_invite_v1(auth_id, channel_id, u_id)


def channel_join_v2(token, channel_id):
    """Join a user with u_id to a channel with channel_id.

    Arguments:
        token (str) - is a jwt, contains info on person accessing
        channel_id (int) - id of given channel

    Exceptions:
        InputError when any of:
            - channel_id does not refer to a valid channel
            - the authorised user is already a member of the channel

          AccessError when:
            - channel_id refers to a channel that is private and the
              authorised user is not already a channel member and is
              not a global owner

    Return Value:
        Returns {}
    """
    auth_id = extract_token(token)["u_id"]
    return channel_join_v1(auth_id, channel_id)
