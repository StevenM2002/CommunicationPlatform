from src.data_store import data_store
from src.error import AccessError, InputError
from src.auth import extract_token

def is_valid_user(u_id, user_list):
    valid_user = False
    for user in user_list:
        if u_id == user["u_id"]:
            valid_user = True
    return valid_user


def admin_user_remove_v1(token, u_id):
    store = data_store.get()
    user_list = store["users"]
    auth_user_id = extract_token(token)["u_id"]
    if auth_user_id not in store["global_owners"]:
        raise AccessError("the authorised user is not a global owner")
    if not is_valid_user(u_id, user_list):
        raise InputError("u_id does not refer to a valid user")
    if u_id in store["global_owners"] and len(store["global_owners"]) == 1:
        raise InputError("u_id refers to a user who is the only global owner")
    for channels in store["channels"]:
        for message in channels["messages"]:
            if message["u_id"] == u_id:
                message["message"] = "Removed user"
        if u_id in channels["all_members"]:
            channels["all_members"].remove(u_id)
        if u_id in channels["owner_members"]:
            channels["owner_members"].remove(u_id)
    for users in store["users"]:
        if users["u_id"] == u_id:
            users["name_first"] = "Removed"
            users["name_last"] = "user"
            store["users"].remove(users)
            store["removed_users"].append(users)
    dms = store["dms"]
    for dm in dms:
        for message in dm["messages"]:
            if message["u_id"] == u_id:
                message["message"] = "Removed user"
        if u_id == dm["owner"]:
            dm["owner"] = -1
        if u_id in dm["members"]:
            dm["members"].remove(u_id)
    data_store.set(store)
    return {}


def admin_user_permission_change_v1(token, u_id, permission_id):
    store = data_store.get()
    user_list = store["users"]
    auth_user_id = extract_token(token)["u_id"]
    if auth_user_id not in store["global_owners"]:
        raise AccessError("the authorised user is not a global owner")
    if not is_valid_user(u_id, user_list):
        raise InputError("u_id does not refer to a valid user")
    if (
        u_id in store["global_owners"]
        and len(store["global_owners"]) == 1
        and permission_id == 2
    ):
        raise InputError(
            "u_id refers to a user who is the only global owner \
            and they are being demoted to a user"
        )
    if permission_id != 1 and permission_id != 2:
        raise InputError("permission_id is invalid")

    user_global_owner = u_id in store["global_owners"]
    if permission_id == 1:
        if not user_global_owner:
            store["global_owners"].append(u_id)
    else:
        if user_global_owner:
            store["global_owners"].remove(u_id)
    data_store.set(store)
    return {}