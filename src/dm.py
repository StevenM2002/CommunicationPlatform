from src.data_store import data_store
from src.error import InputError, AccessError


def dm_create_v1(token, u_ids):
    return {dm_id}


def dm_list_v1(token):
    return {dms}


def dm_remove_v1(token, dm_id):
    return {}


def dm_details_v1(token, dm_id):
    return {name, members}


def dm_leave_v1(token, dm_id):
    return {}


def dm_messages_v1(token, dm_id, start):
    return {messages, start, end}