import math
import time
from src.data_store import data_store
from src.error import InputError, AccessError
from src.auth import extract_token
from src.notifications import add_added_to_a_channel_or_dm_to_notif

OUTPUT_KEYS = ["name", "dm_id"]
USER_KEYS = ["u_id", "email", "name_first", "name_last", "handle_str"]


def dm_create_v1(token, u_ids):
    """Create a new dm

    A new dm will be created with owner who is suppplied token and members which are in u_ids

    Arguments:
        token (str) - An encoded JWT token
        u_ids (list) - a list of auth_user_ids

    Exceptions:
        InputError - Occurs when:
            - any u_id in u_ids does not refer to a valid user

    Return Value:
        Returns { dm_id } on successful dm creation
    """
    store = data_store.get()
    users = store["users"]
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = extract_token(token)
    # check if users in list are valid
    for u_id in u_ids:
        if not any([True for user in users if user["u_id"] == u_id]):
            raise InputError(description="Not valid user to add to dm")
    # sort names to alphabetical order
    handle_list = sorted(
        [
            user["handle_str"]
            for user in users
            if user["u_id"] in u_ids or user["u_id"] == token_data["u_id"]
        ]
    )
    name = ", ".join(handle_list)

    # set new dm_id to 1 + max current id
    store["max_ids"]["dm"] += 1
    data_store.set(store)
    dm_id = store["max_ids"]["dm"]

    dms.append(
        {
            "name": name,
            "dm_id": dm_id,
            "members": list(set(u_ids + [token_data["u_id"]])),
            "messages": [],
            "owner": token_data["u_id"],
        }
    )

    # incrementing the user stats for the owner
    u_ids.append(token_data["u_id"])
    for u_id in u_ids:
        increment_user_dms(u_id)

    # incrementing the workspace stats
    increment_workspace_dms()

    data_store.set(store)
    for u_id in u_ids:
        add_added_to_a_channel_or_dm_to_notif(token_data["u_id"], u_id, -1, dm_id)
    return {"dm_id": dm_id}


def dm_list_v1(token):
    """
    Returns the list of DMs that the user is a member of.

    Arguments:
        token (str) - An encoded JWT token

    Return Value:
        Returns { dms } on success
    """
    store = data_store.get()
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = extract_token(token)

    # loop through dms and add to list if in
    member_dms = [
        {key: dm[key] for key in dm if key in OUTPUT_KEYS}
        for dm in dms
        if token_data["u_id"] in dm["members"]
    ]

    return {"dms": member_dms}


def dm_remove_v1(token, dm_id):
    """
    Remove an existing DM, so all members are no longer in the DM.
    This can only be done by the original creator of the DM.

    Arguments:
        token (str) - An encoded JWT token
        dm_id (int) - the id a dm

    Exceptions:
        InputError - Occurs when:
            - dm_id does not refer to a valid DM
        AcessError - Occurs when:
            - dm_id is valid and the authorised user is not the original DM creator
    """
    store = data_store.get()
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = extract_token(token)

    selected_dm = [dm for dm in dms if dm["dm_id"] == dm_id]

    if len(selected_dm) == 0:
        raise InputError(description="Invalid dm_id")
    selected_dm = selected_dm[0]

    if token_data["u_id"] not in selected_dm["members"]:
        raise AccessError(description="User not in DM")

    if token_data["u_id"] != selected_dm["owner"]:
        raise AccessError(description="User is not DM owner")

    store["dms"] = [dm for dm in dms if dm is not selected_dm]

    # Decrementing user stats
    found_dm = [dm for dm in dms if dm["dm_id"] == dm_id][0]
    members = found_dm["members"]
    for member in members:
        decrement_user_dms(member)

    # Decrement workspace stats
    decrement_workspace_dms()

    data_store.set(store)

    return {}


def dm_details_v1(token, dm_id):
    """Given a DM with ID dm_id that the authorised user is a member of,
    provide basic details about the DM.

    Arguments:
        token (str) - An encoded JWT token
        dm_id (int) - the id a dm

    Exceptions:
        InputError - Occurs when:
            - dm_id does not refer to a valid DM
        AccessError - Occurs when:
            - dm_id is valid and the authorised user is not a member of the DM

    Return Value:
        Returns { name, members } on success
    """
    store = data_store.get()
    users = store["users"]
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = extract_token(token)

    selected_dm = [dm for dm in dms if dm["dm_id"] == dm_id]

    if len(selected_dm) == 0:
        raise InputError(description="Invalid dm_id")
    selected_dm = selected_dm[0]

    if token_data["u_id"] not in selected_dm["members"]:
        raise AccessError(description="User not in DM")
    members_detail = [
        {key: user[key] for key in user if key in USER_KEYS}
        for user in users
        if user["u_id"] in selected_dm["members"]
    ]

    return {"name": selected_dm["name"], "members": members_detail}


def dm_leave_v1(token, dm_id):
    """
    Given a DM ID, the user is removed as a member of this DM.

    Arguments:
        token (str) - An encoded JWT token
        dm_id (int) - the id a dm

    Exceptions:
        InputError - Occurs when:
            - dm_id does not refer to a valid DM
        AccessError - Occurs when:
            - dm_id is valid and the authorised user is not a member of the DM
    """
    store = data_store.get()
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = extract_token(token)

    selected_dm = [dm for dm in dms if dm["dm_id"] == dm_id]

    if len(selected_dm) == 0:
        raise InputError(description="Invalid dm_id")
    selected_dm = selected_dm[0]

    if token_data["u_id"] not in selected_dm["members"]:
        raise AccessError(description="User not in DM")
    selected_dm["members"].remove(token_data["u_id"])

    # Updating the user stats
    decrement_user_dms(token_data["u_id"])

    # if no members left in dm delete dm
    if len(selected_dm["members"]) == 0:
        store["dms"] = [dm for dm in dms if dm is not selected_dm]
        # Updating workspace stats
        decrement_workspace_dms()

    data_store.set(store)

    return {}


def dm_messages_v1(token, dm_id, start):
    """Given a DM with ID dm_id that the authorised user is a member of,
    return up to 50 messages between index "start" and "start + 50".

    Arguments:
        token (str) - An encoded JWT token
        dm_id (int) - the id a dm
        start (int) - the message to start retrieving from (0 is most recent)

    Exceptions:
        InputError - Occurs when:
            - dm_id does not refer to a valid DM
            - start is greater than the total number of messages in the channel
        AccessError - Occurs when:
            - dm_id is valid and the authorised user is not a member of the DM

    Return Value:
        Returns { messsages, start, end } on successful dm creation
    """
    store = data_store.get()
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = extract_token(token)

    selected_dm = [dm for dm in dms if dm["dm_id"] == dm_id]

    if len(selected_dm) == 0:
        raise InputError(description="Invalid dm_id")
    selected_dm = selected_dm[0]

    if token_data["u_id"] not in selected_dm["members"]:
        raise AccessError(description="User not in DM")
    messages = selected_dm["messages"]

    if start + 1 > len(messages) and start != 0:
        raise InputError(description="Start index larger than number of messages")

    return {
        "messages": messages[start : start + 50],
        "start": start,
        "end": start + 50 if start + 50 < len(messages) else -1,
    }


def increment_workspace_dms():
    # Fetching the data store
    store = data_store.get()
    workspace = store["workspace_stats"]

    # Creating a timestamp and incrementing the workspace stats
    timestamp = math.floor(time.time())
    num_dms = workspace["dms_exist"][-1]["num_dms_exist"]
    workspace["dms_exist"].append(
        {"num_dms_exist": num_dms + 1, "time_stamp": timestamp}
    )


def decrement_workspace_dms():
    # Fetching the data store
    store = data_store.get()
    workspace = store["workspace_stats"]

    # Creating a timestamp and decrementing the workspace stats
    timestamp = math.floor(time.time())
    num_dms = workspace["dms_exist"][-1]["num_dms_exist"]
    workspace["dms_exist"].append(
        {"num_dms_exist": num_dms - 1, "time_stamp": timestamp}
    )


def increment_user_dms(u_id):
    # Fetching the data store
    users = data_store.get()["users"]

    # Creating a timestamp
    timestamp = math.floor(time.time())

    # Finding the required user to increment stats
    found_user = [user for user in users if user["u_id"] == u_id][0]

    # Increments the user stats
    user_stats = found_user["user_stats"]
    dms_joined_prev = user_stats["dms_joined"][-1]["num_dms_joined"]
    user_stats["dms_joined"].append(
        {"num_dms_joined": dms_joined_prev + 1, "time_stamp": timestamp}
    )


def decrement_user_dms(u_id):
    # Fetching the data store
    users = data_store.get()["users"]

    # Creating a timestamp
    timestamp = math.floor(time.time())

    # Finding the required user to decrement stats
    found_user = [user for user in users if user["u_id"] == u_id][0]

    # Decrements the user stats
    user_stats = found_user["user_stats"]
    dms_joined_prev = user_stats["dms_joined"][-1]["num_dms_joined"]
    user_stats["dms_joined"].append(
        {"num_dms_joined": dms_joined_prev - 1, "time_stamp": timestamp}
    )
