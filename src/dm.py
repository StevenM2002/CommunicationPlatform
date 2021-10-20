import jwt

from src.data_store import data_store
from src.error import InputError, AccessError
from src.auth import JWT_SECRET

OUTPUT_KEYS = ["name", "dm_id"]
USER_KEYS = ["u_id", "email", "name_first", "name_last", "handle_str"]


def dm_create_v1(token, u_ids):
    store = data_store.get()
    users = store["users"]
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    valid_token = any(
        [
            True
            for user in users
            if token_data["u_id"] == user["u_id"]
            and token_data["session_id"] in user["session_ids"]
        ]
    )
    if not valid_token:
        raise AccessError(description="Invalid Token")
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

    dm_id = max(dms, key=lambda x: x["dm_id"])["dm_id"] + 1 if len(dms) > 0 else 0

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
    store = data_store.get()
    users = store["users"]
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    valid_token = any(
        [
            True
            for user in users
            if token_data["u_id"] == user["u_id"]
            and token_data["session_id"] in user["session_ids"]
        ]
    )
    if not valid_token:
        raise AccessError(description="Invalid Token")
    member_dms = [
        {key: dm[key] for key in dm if key in OUTPUT_KEYS}
        for dm in dms
        if token_data["u_id"] in dm["members"]
    ]

    return {"dms": member_dms}


def dm_remove_v1(token, dm_id):
    store = data_store.get()
    users = store["users"]
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    valid_token = any(
        [
            True
            for user in users
            if token_data["u_id"] == user["u_id"]
            and token_data["session_id"] in user["session_ids"]
        ]
    )
    if not valid_token:
        raise AccessError(description="Invalid Token")
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
    store = data_store.get()
    users = store["users"]
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    valid_token = any(
        [
            True
            for user in users
            if token_data["u_id"] == user["u_id"]
            and token_data["session_id"] in user["session_ids"]
        ]
    )
    if not valid_token:
        raise AccessError(description="Invalid Token")
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
    store = data_store.get()
    users = store["users"]
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    valid_token = any(
        [
            True
            for user in users
            if token_data["u_id"] == user["u_id"]
            and token_data["session_id"] in user["session_ids"]
        ]
    )
    if not valid_token:
        raise AccessError(description="Invalid Token")
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
    store = data_store.get()
    users = store["users"]
    dms = store["dms"]  # [{ dm_id, name },]
    token_data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    valid_token = any(
        [
            True
            for user in users
            if token_data["u_id"] == user["u_id"]
            and token_data["session_id"] in user["session_ids"]
        ]
    )

    if not valid_token:
        raise AccessError(description="Invalid Token")
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
