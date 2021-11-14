import math
import time
from collections import defaultdict

from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import first
from src.notifications import add_tagged_to_notif

VALID_REACT_IDS = (1,)


def create_message(message_text, message_id, user_id):
    return {
        "message": message_text,
        "message_id": message_id,
        "time_created": math.floor(time.time()),
        "u_id": user_id,
        "reacts": defaultdict(list),
        "is_pinned": False,
    }


def get_message(message_id):
    """Get a message from a message id"""
    data = data_store.get()
    for group in (*data["channels"], *data["dms"]):
        for message in group["messages"]:
            if message["message_id"] == message_id:
                return message, group

    raise InputError("no message with message id was found")


def owner_perms(user_id, group):
    data = data_store.get()
    global_owner = user_id in data["global_owners"]
    if "dm_id" in group:
        authorised = user_id == group["owner"]
    else:
        authorised = user_id in group["owner_members"] or global_owner

    return authorised


def is_member(user_id, group):
    if "dm_id" in group:
        return user_id == group["owner"] or user_id in group["members"]
    else:
        return user_id in group["owner_members"] or user_id in group["all_members"]


def channel_messages_v1(auth_user_id, channel_id, start):
    """Get the messages from a channels.

    Arguments:
        auth_user_id (int) - id of user requesting messages
        channel_id (int) - id of channel to get messages from
        start (int) - index of first message to start from

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
    messages = len(channel["messages"])
    if start > messages:
        raise InputError("start message id is greater than latest message id")

    # end is set to -1 if the most recent message has been returned
    return {
        "messages": channel["messages"][start : start + 50],
        "start": start,
        "end": start + 50 if start + 50 < messages else -1,
    }


def message_send_v1(user_id, channel_id, message_text):
    """Send a message from use to a channel.

    Arguments:
        user_id (int) - id of user requesting messages
        channel_id (int) - id of channel to get messages from
        message_text (str) - index of first message to start from

    Exceptions:
        InputError when:
            - channel_id does not refer to a valid channel
            - length of message is less than 1 or over 1000 characters
        AccessError when:
            - channel_id is valid and the authorised user is not a member of the channel

    Returns:
        Returns {message_id}
    """
    data = data_store.get()
    channel = first(lambda c: c["channel_id"] == channel_id, data["channels"], {})

    if not channel:
        raise InputError("no channel matching channel id")
    if not user_id in channel["all_members"]:
        raise AccessError("user is not a member of this channel")
    if not 1 <= len(message_text) <= 1000:
        raise InputError("message must be between 1 and 1000 characters")

    message_id = data["max_ids"]["message"] + 1
    data["max_ids"]["message"] += 1
    message = create_message(message_text, message_id, user_id)
    channel["messages"].insert(0, message)
    data_store.set(data)
    add_tagged_to_notif(user_id, channel_id, -1, message_text)

    return {"message_id": message_id}


def message_edit_v1(user_id, message_id, edited_message):
    """Edit a message with message_id to say edited_message.

    Arguments:
        user_id (int) - id of user requesting messages
        message_id (int) - id of channel to get messages from
        edited_message (str) - index of first message to start from

    Exceptions:
        InputError when:
            - length of message is over 1000 characters
            - message_id does not refer to a valid message within a
              channel/DM that the authorised user has joined

        AccessError when:
            - message_id refers to a valid message in a joined
              channel/DM and none of the following are true
            - the message was sent by the authorised user making this
              request
            - the authorised user has owner permissions in the channel/DM

    Returns:
        Returns {}
    """
    message, group = get_message(message_id)
    authorised = owner_perms(user_id, group)

    if message["u_id"] != user_id and not authorised:
        raise AccessError("user not authorised to edit message")
    if len(edited_message) > 1000:
        raise InputError("message longer than 1000 characters")
    if edited_message == "":
        message_remove_v1(user_id, message_id)
    else:
        message["message"] = edited_message
    return {}


def message_remove_v1(user_id, message_id):
    """Remove a message with message_id from user_id.

    Arguments:
        user_id (int) - id of user requesting messages
        message_id (int) - id of message to remove

    Exceptions:
        InputError when:
            - message_id does not refer to a valid message within a
              channel/DM that the authorised user has joined
        AccessError when:
            - message_id refers to a valid message in a joined
              channel/DM and none of the following are true
            - the message was sent by the authorised user making this
              request
            - the authorised user has owner permissions in the channel/DM

    Returns:
        Returns {}
    """
    message, group = get_message(message_id)
    authorised = owner_perms(user_id, group)

    if message["u_id"] != user_id and not authorised:
        raise AccessError("user not authorised to edit message")
    group["messages"].remove(message)
    return {}


def message_senddm_v1(user_id, dm_id, message_text):
    """Send a dm in dm_id with message_text to user_id.

    Arguments:
        user_id (int) - id of user requesting messages
        channel_id (int) - id of channel to get messages from
        message_text (str) - index of first message to start from

    Exceptions:
        InputError when:
            - message_id does not refer to a valid message within a
              channel/DM that the authorised user has joined
        AccessError when:
            - message_id refers to a valid message in a joined channel/DM
              and none of the following are true
            - the message was sent by the authorised user making this
              request the authorised user has owner permissions in the
              channel/DM

    Returns:
        Returns {}
    """
    data = data_store.get()
    for dm in data["dms"]:
        if dm["dm_id"] == dm_id:
            if user_id not in dm["members"]:
                raise AccessError("user not a member of dm")
            if not 1 <= len(message_text) <= 1000:
                raise InputError("message must be between 1 and 1000 characters")
            data["max_ids"]["message"] += 1
            message_id = data["max_ids"]["message"]
            data_store.set(data)
            message = create_message(message_text, message_id, user_id)
            dm["messages"].insert(0, message)
            add_tagged_to_notif(user_id, -1, dm_id, message_text)
            return {"message_id": message_id}

    raise InputError("no dm matching dm id")


def message_react_v1(auth_user_id, message_id, react_id):
    message, group = get_message(message_id)
    member = is_member(auth_user_id, group)

    if not member:
        raise InputError("user not a member of group")
    if react_id not in VALID_REACT_IDS:
        raise InputError("invalid react_id")
    if (
        auth_user_id in message["reacts"]
        and react_id in message["reacts"][auth_user_id]
    ):
        raise InputError("message already contains reaction from user")

    message["reacts"][auth_user_id].append(react_id)

    return {}


def message_unreact_v1(auth_user_id, message_id, react_id):
    message, group = get_message(message_id)
    member = is_member(auth_user_id, group)

    if not member:
        raise InputError("user not a member of group")
    if react_id not in VALID_REACT_IDS:
        raise InputError("invalid react_id")
    if auth_user_id not in message["reacts"]:
        raise InputError("message does not contain a reaction")

    message["reacts"][auth_user_id].remove(react_id)

    return {}


def message_pin_v1(auth_user_id, message_id):
    message, group = get_message(message_id)
    authorised = owner_perms(auth_user_id, group)

    if not authorised:
        raise AccessError("user does not have owner permissions in group")
    if message["is_pinned"]:
        raise InputError("message already pinned")

    message["is_pinned"] = True

    return {}


def message_unpin_v1(auth_user_id, message_id):
    message, group = get_message(message_id)
    authorised = owner_perms(auth_user_id, group)

    if not authorised:
        raise AccessError("user does not have owner permissions in group")
    if not message["is_pinned"]:
        raise InputError("message already unpinned")

    message["is_pinned"] = False

    return {}
