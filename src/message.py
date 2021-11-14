import math
import time
from threading import Timer

from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import first
from src.notifications import add_tagged_to_notif
from src.notifications import add_reacted_msg_to_notif


VALID_REACT_ID = 1


def create_message(message_text, message_id, user_id):
    return {
        "message": message_text,
        "message_id": message_id,
        "time_created": math.floor(time.time()),
        "u_id": user_id,
        "reacts": [{"react_id": VALID_REACT_ID, "u_ids": []}],
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

    # add is_this_user_reacted key to reactions
    for message in channel["messages"]:
        message["reacts"][0]["is_this_user_reacted"] = (
            auth_user_id in message["reacts"][0]["u_ids"]
        )

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
    if react_id != VALID_REACT_ID:
        raise InputError("invalid react_id")
    if auth_user_id in message["reacts"][0]["u_ids"]:
        raise InputError("message already contains reaction from user")
    message["reacts"][0]["u_ids"].append(auth_user_id)
    channel_id = -1 if "channel_id" not in group else group["channel_id"]
    dm_id = -1 if "dm_id" not in group else group["dm_id"]
    add_reacted_msg_to_notif(auth_user_id, message["u_id"], channel_id, dm_id)

    return {}


def message_unreact_v1(auth_user_id, message_id, react_id):
    message, group = get_message(message_id)
    member = is_member(auth_user_id, group)

    if not member:
        raise InputError("user not a member of group")
    if react_id != VALID_REACT_ID:
        raise InputError("invalid react_id")
    if auth_user_id not in message["reacts"][0]["u_ids"]:
        raise InputError("message does not contain a reaction")

    message["reacts"][0]["u_ids"].remove(auth_user_id)

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


def message_share_v1(user_id, og_message_id, message, channel_id, dm_id):
    data = data_store.get()
    channel = first(lambda c: c["channel_id"] == channel_id, data["channels"], {})
    dm = first(lambda c: c["dm_id"] == dm_id, data["dms"], {})
    og_message, message_group = get_message(og_message_id)

    if not dm and not channel:
        raise InputError("invalid dm id and channel id")
    if channel and not is_member(user_id, channel):
        raise AccessError("user not member of channel")
    if dm and not is_member(user_id, dm):
        raise AccessError("user not member of dm")
    if not is_member(user_id, message_group):
        raise InputError("message not from channel user has joined")
    if dm_id != -1 and channel_id != -1:
        raise InputError("either channel id or dm id")
    if not len(message) <= 1000:
        raise InputError("message is longer than 1000 characters")

    message_text = og_message["message"]
    if len(message) > 0:
        message_text += f", {message}"

    message_id = data["max_ids"]["message"] + 1
    data["max_ids"]["message"] += 1
    data_store.set(data)

    if channel:
        send_channel_message(channel_id, message_text, message_id, user_id)
    if dm:
        send_dm_message(dm_id, message_text, message_id, user_id)

    return {"shared_message_id": message_id}


def message_sendlater(user_id, channel_id, message, time_sent):
    data = data_store.get()
    channel = first(lambda c: c["channel_id"] == channel_id, data["channels"], {})

    if not channel:
        raise InputError("no channel matching channel id")
    if not user_id in channel["all_members"]:
        raise AccessError("user is not a member of this channel")
    if not 1 <= len(message) <= 1000:
        raise InputError("message must be between 1 and 1000 characters")
    now = time.time()
    if time_sent < now:
        raise InputError("time_sent is in the past")

    message_id = data["max_ids"]["message"] + 1
    data["max_ids"]["message"] += 1
    data_store.set(data)

    t = Timer(
        time_sent - now,
        send_channel_message,
        (channel_id, message, message_id, user_id),
    )
    t.start()

    return {"message_id": message_id}


def message_sendlater_dm(user_id, dm_id, message, time_sent):
    data = data_store.get()
    dm = first(lambda c: c["dm_id"] == dm_id, data["dms"], {})

    if not dm:
        raise InputError("no dm matching dm id")
    if not user_id in dm["members"]:
        raise AccessError("user is not a member of this channel")
    if not 1 <= len(message) <= 1000:
        raise InputError("message must be between 1 and 1000 characters")
    now = time.time()
    if time_sent < now:
        raise InputError("time_sent is in the past")

    message_id = data["max_ids"]["message"] + 1
    data["max_ids"]["message"] += 1
    data_store.set(data)

    t = Timer(
        time_sent - now,
        send_dm_message,
        (dm_id, message, message_id, user_id),
    )
    t.start()

    return {"message_id": message_id}


def send_channel_message(channel_id, message, message_id, user_id):
    data = data_store.get()
    removed = first(lambda u: u["u_id"] == user_id, data["removed_users"], {})
    if removed:
        message = "Removed user"
    channel = first(lambda c: c["channel_id"] == channel_id, data["channels"], {})
    message = create_message(message, message_id, user_id)
    channel["messages"].insert(0, message)
    data_store.set(data)


def send_dm_message(dm_id, message, message_id, user_id):
    data = data_store.get()
    removed = first(lambda u: u["u_id"] == user_id, data["removed_users"], {})
    if removed:
        message = "Removed user"
    dm = first(lambda d: d["dm_id"] == dm_id, data["dms"], {})
    message = create_message(message, message_id, user_id)
    dm["messages"].insert(0, message)
    data_store.set(data)
