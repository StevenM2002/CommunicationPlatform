from src.auth import extract_token
from src.error import AccessError, InputError
from src.data_store import data_store


def search_v1(token, query_str):
    """
    {message_id, u_id, message, time_created, reacts, is_pinned}
    """

    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError("query_str len not valid")

    u_id = extract_token(token)["u_id"]
    messages_ret = []
    store = data_store.get()
    channel_list = store["channels"]
    dms_list = store["dms"]

    for channel in channel_list:
        if u_id in channel["all_members"]:
            for messages in channel["messages"]:
                if query_str in messages["message"]:
                    messages_ret.append(messages)

    for dms in dms_list:
        if u_id in dms["members"]:
            for dm_msg in dms["messages"]:
                if query_str in dm_msg["message"]:
                    messages_ret.append(dm_msg)

    return {"messages": messages_ret}
