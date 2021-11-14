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
            "handle_str": handle,
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
from copy import deepcopy
from json import dump, load
from pathlib import Path
from threading import Event, Thread


INITIAL_OBJECT = {
    "users": [],
    "channels": [],
    "global_owners": [],
    "removed_users": [],
    "dms": [],
    "standups": [],
    "max_ids": {"dm": -1, "message": -1, "channel": -1, "user": -1},
    "all_notifications": [],
}
DATA_STORE_FILE = "datastore.json"
WRITE_INTERVAL = 30


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
    data_store.set(deepcopy(INITIAL_OBJECT))
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
