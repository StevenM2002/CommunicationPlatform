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

INITIAL_OBJECT = {"users": [], "channels": [], "global_owners": []}


class Datastore:
    """Datastore class used to store data for Streams."""

    def __init__(self):
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


data_store = Datastore()
