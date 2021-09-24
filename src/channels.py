from src.data_store import data_store
def channels_list_v1(auth_user_id):
    initial_object = data_store.get()
    # If no channels then return None
    if len(initial_object["channels"]) == 0:
        return None
    # Initialise a channel to append channel information to after finding a channel the auth_user_id is in
    channels = []
    for channel in range(len(initial_object["channels"])):
        # Get route to all channels
        channels_list = initial_object["channels"][channel]
        for members in range(len(channels_list["all_members"])):
            # Save channel information
            ch_id = channels_list["channel_id"]
            ch_name = channels_list["name"]
            # If auth_user_id is matched with a u_id in a channel, then append saved channel information into channels list
            if channels_list["all_members"][members]["u_id"] == 1:
                channels.append({"channel_id": ch_id, "name": ch_name})
    # If auth_user_id is not part of any channel, then None is returned or else, return the channels they are in
    if len(channels) == 0:
        return None
    else:
        return {"channels": channels}
    
'''
def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }
'''
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
    return {
        'channel_id': 1,
    }
