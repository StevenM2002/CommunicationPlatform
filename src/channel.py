from src.data_store import data_store
from src.error import AccessError, InputError
def channel_invite_v1(auth_user_id, channel_id, u_id):
    
    store = data_store.get()
    channel_list = store["channels"]
    user_list = store["users"]

    valid_channel = False
    for each_channel in channel_list:
        if (each_channel["channel_id"] == channel_id):
            valid_channel = True
            channel = each_channel
    if (valid_channel == False):
        raise InputError("channel_id does not refer to a valid channel")

    valid_user = False
    for each_user in user_list:
        if (each_user["u_id"] == u_id):
            user_to_add = each_user
            valid_user = True
    if (valid_user == False):
        raise InputError("u_id does not refer to a valid user")

    valid_member = False
    uid_in_channel = False
    for users in channel["members"]:
        if (users == auth_user_id):
            valid_member = True
        if (users == u_id):
            uid_in_channel = True
    if (valid_member == False):
        raise AccessError("the authorised user is not a member of the channel")
    if (uid_in_channel == True):
        raise InputError("u_id refers to a user who is already a member of \
            the channel")
            
    channel["members"].append(user_to_add["u_id"])
    print(f"user id is {user_to_add}")
    return {

    }

def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    #placeholder for testing

    store = data_store.get()

    for users in store["users"]:
        if (users["u_id"] == auth_user_id):
            to_add = users
    for channels in store["channels"]:
        if (channels["id"] == channel_id):
            to_add_to = channels
    
    to_add_to.append(to_add)
    return {

    }
