"""Responsible for storing all the data in the Streams databse.

This contains a definition for the Datastore class which stores all the data
for the Streams database. This database can be accessed using the data_store
variable which is an instance of the Datastore class. It follows the following
data structure:
{
    "users": [
        {
            "u_id": user_id,
            "email": email,
            "password": password,
            "name_first": name_first,
            "name_last": name_last,
            "profile_img_url": img_url,
            "handle_str": handle,
            "user_stats": 
                {
                    channels_joined: [{num_channels_joined, time_stamp}],
                    dms_joined: [{num_dms_joined, time_stamp}], 
                    messages_sent: [{num_messages_sent, time_stamp}], 
                }
            "session_ids": [session_id]
            "reset_codes": [reset_code]
        },
        ...
    ],
    "channels":[
        {
            "channel_id": channel_id,
            "name": name,
            "owner_members": [auth_user_id],
            "all_members": [auth_user_id],
            "is_public": is_public,
            "messages": [],
        },
        ...
    ],
    "global_owners": [auth_user_id],
    "dms" : [
        {
            "dm_id": dm_id,
            "name": name,
            "messages": [],
            "members": [auth_user_id],
            "owner": auth_user_id,
        },
    ],
    "workspace_stats": 
        {
             channels_exist: [{num_channels_exist, time_stamp}], 
             dms_exist: [{num_dms_exist, time_stamp}], 
             messages_exist: [{num_messages_exist, time_stamp}], 
        },
    "all_notifications":[{"u_id": int, "notifications":[]},...]
}

    Typical usage example:

    from data_store import data_store

    store = data_store.get()
    users = store["users"]

    rob = {
        "u_id": 23,
        "email": "rob@gmail.com",
        "password": "password",
        "name_first": "rob",
        "name_last": "scallon",
        "handle_str": "robscallon",
    }
    users.append(rob)
    data_store.set(users)

"""
import time
import math
import os
import shutil
from copy import deepcopy
from json import dump, load
from pathlib import Path
from threading import Event, Thread


timestamp = math.floor(time.time())


INITIAL_OBJECT = {
    "users": [],
    "channels": [],
    "global_owners": [],
    "removed_users": [],
    "dms": [],
    "standups": [],
    "workspace_stats": {
        "channels_exist": [{"num_channels_exist": 0, "time_stamp": timestamp}],
        "dms_exist": [{"num_dms_exist": 0, "time_stamp": timestamp}],
        "messages_exist": [{"num_messages_exist": 0, "time_stamp": timestamp}],
    },
    "max_ids": {"dm": -1, "message": -1, "channel": -1, "user": -1, "reset_id": -1},
    "all_notifications": [],
}
DATA_STORE_FILE = "datastore.json"
WRITE_INTERVAL = 30

IMAGE_FOLDER = "imgfolder"


class Datastore:
    """Datastore class used to store data for Streams."""

    def __init__(self):
        if Path(DATA_STORE_FILE).is_file():
            try:
                self.__store = load(open(DATA_STORE_FILE))
            except:
                self.__store = deepcopy(INITIAL_OBJECT)
        else:
            self.__store = deepcopy(INITIAL_OBJECT)

        if not Path(IMAGE_FOLDER).is_dir():
            os.mkdir(IMAGE_FOLDER)

    def get(self):
        """Get the dictionary of the data base.

        Return Value:
            Returns datastore (dictionary)"""
        return self.__store

    def set(self, store):
        """Get the dictionary of the data base.

        Arguments:
            store (dictionary) - new data base dictionary

        Exceptions:
            TypeError - Occurs when:
                - store is not a dictionary"""
        if not isinstance(store, dict):
            raise TypeError("store must be of type dictionary")
        self.__store = store


def clear_v1():
    """Clear the datastore class object to the value of INITIAL_OBJECT."""
    timestamp = math.floor(time.time())
    data_store.set(deepcopy(INITIAL_OBJECT))

    # Retrieving the data_store and updating the timestamps for workspace stats
    workspace = data_store.get()["workspace_stats"]
    for it in ("channels_exist", "dms_exist", "messages_exist"):
        workspace[it][0]["time_stamp"] = timestamp
    os.rmdir(IMAGE_FOLDER)
    os.mkdir(IMAGE_FOLDER)

    return {}


def every(interval):
    def decorator(func):
        def wrapper(*args, **kwargs):
            stopped = Event()

            def loop():
                while not stopped.wait(interval):
                    func(*args, **kwargs)

            t = Thread(target=loop)
            t.daemon = True
            t.start()
            return stopped

        return wrapper

    return decorator


@every(WRITE_INTERVAL)
def save_data_store():
    dump(data_store.get(), open(DATA_STORE_FILE, "w"))


data_store = Datastore()
save_data_store()
