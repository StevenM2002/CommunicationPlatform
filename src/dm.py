from src.data_store import data_store
from src.error import InputError, AccessError
from src.auth import extract_token

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
    for u_id in u_ids:
        if not any([True for user in users if user["u_id"] == u_id]):
            raise InputError(description="Not valid user to add to dm")
    handle_list = sorted(
        [
            user["handle_str"]
            for user in users
            if user["u_id"] in u_ids or user["u_id"] == token_data["u_id"]
        ]
    )

    name = ", ".join(handle_list)

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

    data_store.set(store)

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

    if len(selected_dm["members"]) == 0:
        store["dms"] = [dm for dm in dms if dm is not selected_dm]

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
