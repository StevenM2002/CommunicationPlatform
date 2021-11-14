from src.data_store import data_store
import re


def add_new_id_to_notif(u_id):
    """Initialises a new id to the notifications section in datastore

    Arguments:
        u_id (int) - id of a user who's being added to datastore

    Exceptions:
        N/A

    Return Value:
        Returns None
    """
    store = data_store.get()
    store["all_notifications"].append({"u_id": u_id, "notifications": []})
    data_store.set(store)


def add_tagged_to_notif(u_id, ch_id, dm_id, message_text):
    """Checks and adds to notification if a message tags a user

    Arguments:
        u_id (int) - id of a user who's doing the tagging
        ch_id (int) - id of a channel
        dm_id (int) - id of a dm
        message_text (str) - the message being sent

    Exceptions:
        N/A

    Return Value:
        Returns None
    """
    if "@" not in message_text:
        return
    # Get first @ to end of str and split the result by spaces
    split_str = re.search("@.*", message_text).group().split()
    each_yourid = []
    for string in split_str:
        if "@" in string:
            temp = string.split("@")
            for each in temp:
                x = get_u_id_from_handle(each)
                # Append if the u_id is valid
                if x != None:
                    each_yourid.append(x)
    info = get_handle_and_name(u_id, ch_id, dm_id)
    handle = info["handle"]
    name = info["name"]
    message = f"{handle} tagged you in {name}: {message_text[:20]}"
    to_add = {"channel_id": ch_id, "dm_id": dm_id, "notification_message": message}
    for your_id in each_yourid:
        add_to_notif(your_id, to_add)


def add_reacted_msg_to_notif(u_id, your_id, ch_id, dm_id):
    """Adds notification for reacting to a message in a channel or dm

    Arguments:
        u_id (int) - id of a user who's doing the adding
        your_id (int) - id of a user who is being added
        ch_id (int) - id of a channel
        dm_id (int) - id of a dm

    Exceptions:
        N/A

    Return Value:
        Returns None
    """
    info = get_handle_and_name(u_id, ch_id, dm_id)
    handle = info["handle"]
    name = info["name"]
    message = f"{handle} reacted to your message in {name}"
    to_add = {"channel_id": ch_id, "dm_id": dm_id, "notification_message": message}
    add_to_notif(your_id, to_add)


def add_added_to_a_channel_or_dm_to_notif(u_id, your_id, ch_id, dm_id):
    """Adds notification for added to a channel or dm

    Arguments:
        u_id (int) - id of a user who's doing the adding
        your_id (int) - id of a user who is being added
        ch_id (int) - id of a channel
        dm_id (int) - id of a dm

    Exceptions:
        N/A

    Return Value:
        Returns None
    """
    info = get_handle_and_name(u_id, ch_id, dm_id)
    handle = info["handle"]
    name = info["name"]
    message = f"{handle} added you to {name}"
    to_add = {"channel_id": ch_id, "dm_id": dm_id, "notification_message": message}
    add_to_notif(your_id, to_add)


def get_u_id_from_handle(handle):
    """gets the u_id from a given handle

    Arguments:
        handle (str) - the handle of a user

    Exceptions:
        N/A

    Return Value:
        Returns return user["u_id"] or None
    """
    store = data_store.get()
    for user in store["users"]:
        if user["handle_str"] == handle:
            return user["u_id"]


def get_handle_and_name(u_id, ch_id, dm_id):
    """Gets the handle of u_id and name of channel or dm

    Arguments:
        u_id (int) - id of a user who's hande is being retrieved
        ch_id (int) - id of a channel
        dm_id (int) - id of a dm

    Exceptions:
        N/A

    Return Value:
        Returns {"handle": handle, "name": name}
    """
    store = data_store.get()
    all_users = store["users"]
    handle = None
    for user in all_users:
        if user["u_id"] == u_id:
            handle = user["handle_str"]
    name = None
    all_channels = store["channels"]
    for channel in all_channels:
        if channel["channel_id"] == ch_id:
            name = channel["name"]
            break
    all_dms = store["dms"]
    for dm in all_dms:
        if dm["dm_id"] == dm_id:
            name = dm["name"]
            break
    return {"handle": handle, "name": name}


def add_to_notif(u_id, to_add):
    """Adds notification to datastore

    Arguments:
        u_id (int) - id of a user who's notifications is being added
        to_add (str) - the message to be appended

    Exceptions:
        N/A

    Return Value:
        None
    """
    store = data_store.get()
    notifs = store["all_notifications"]
    for notif in notifs:
        if notif["u_id"] == u_id:
            if len(notif["notifications"]) >= 20:
                notif["notifications"].pop(0)
            notif["notifications"].append(to_add)

    data_store.set(store)


def notifications_get_v1(u_id):
    """Gets the last 20 notifications of a user

    Arguments:
        u_id (int) - id of a user who's notifications is being retrieved

    Exceptions:
        N/A

    Return Value:
        Returns {"notifications": [{messages}]}
    """
    store = data_store.get()
    notifs = store["all_notifications"]
    ret_msg = []
    for notif in notifs:
        if notif["u_id"] == u_id:
            ret_msg = notif["notifications"][::-1]
    return {"notifications": ret_msg}
