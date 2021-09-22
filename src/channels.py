from data_store import data_store
from src.error import InputError, AccessError

def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create_v1(auth_user_id, name, is_public):
    # Retrieves the data store, and the channel dictionary
    store = data_store.get()
    users = store['users']
    channels = store['channels']
    # Determines if the auth_user_id is valid by iterating through the names list
    valid = 0
    for item in users:
        if item['id'] == auth_user_id:
            valid = 1
    # Returns an error if this function is invalid
    if valid == 0:
        # Not completely sure what to include as the exception datatype yet
        AccessError(auth_user_id)

    # Iterates through the channels list to determine the next available index
    # Creates the new list when an available index is found
    for i in range(len(channels) + 1):
        found = 0
        for item in channels:
            if item['channel_id'] == i:
                found = 1
        if found == 0:
            id = i
            # If the given id is not found, then the new channel is given that id
            channels.append[{
                'id': i,
                'name': name,
                'owner': auth_user_id
            }]
            break

    return {
        'channel_id': id,
    }
