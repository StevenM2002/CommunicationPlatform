import math
import time

from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import first


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
        raise InputError(description="no channel matching channel id")
    if not auth_user_id in channel["all_members"]:
        raise AccessError(description="user is not a member of this channel")
    messages = len(channel["messages"])
    if start > messages:
        raise InputError(
            description="start message id is greater than latest message id"
        )

    # end is set to -1 if the most recent message has been returned
    return {
        "messages": channel["messages"][start : start + 50],
        "start": start,
        "end": start + 50 if start + 50 < messages else -1,
    }


def message_send_v1(user_id, channel_id, message_text):
    data = data_store.get()
    channel = first(lambda c: c["channel_id"] == channel_id, data["channels"], {})
    if not channel:
        raise InputError(description="no channel matching channel id")
    if not user_id in channel["all_members"]:
        raise AccessError(description="user is not a member of this channel")
    if not 1 <= len(message_text) <= 1000:
        raise InputError(description="message must be between 1 and 1000 characters")
    message_id = data["max_ids"]["message"] + 1
    data["max_ids"]["message"] += 1
    message = {
        "message": message_text,
        "message_id": message_id,
        "time_created": math.floor(time.time()),
        "u_id": user_id,
    }
    channel["messages"].insert(0, message)
    data_store.set(data)
    return {"message_id": message_id}


def get_message(message_id):
    data = data_store.get()
    for group in (*data["channels"], *data["dms"]):
        for message in group["messages"]:
            if message["message_id"] == message_id:
                return message, group
    raise InputError(description="no message with message id was found")


def message_edit_v1(user_id, message_id, edited_message):
    message, group = get_message(message_id)
    if message["u_id"] != user_id and user_id not in group["owner_members"]:
        raise AccessError(
            description="message not sent by user or user not owner of channel"
        )
    if len(edited_message) > 1000:
        raise InputError(description="message longer than 1000 characters")
    if edited_message == "":
        message_remove_v1(user_id, message_id)
    else:
        message["message"] = edited_message
    return {}


def message_remove_v1(user_id, message_id):
    message, group = get_message(message_id)
    if message["u_id"] != user_id and user_id not in group["owner_members"]:
        raise AccessError(
            description="message not sent by user or user not owner of channel"
        )
    group["messages"].remove(message)
    return {}


def message_senddm_v1(user_id, dm_id, message_text):
    data = data_store.get()
    for dm in data["dms"]:
        if dm["dm_id"] == dm_id:
            if user_id not in dm["members"]:
                raise AccessError(description="user not a member of dm")
            if not 1 <= len(message_text) <= 1000:
                raise InputError(
                    description="message must be between 1 and 1000 characters"
                )
            data["max_ids"]["message"] += 1
            message_id = data["max_ids"]["message"]
            data_store.set(data)
            message = {
                "message": message_text,
                "message_id": message_id,
                "time_created": math.floor(time.time()),
                "u_id": user_id,
            }
            dm["messages"].insert(0, message)
            return {"message_id": message_id}
    raise InputError(description="no dm matching dm id")
