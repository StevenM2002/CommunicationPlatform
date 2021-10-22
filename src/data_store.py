"""Responsible for storing all the data in the Streams databse.

This contains a definition for the Datastore class which stores all the data
for the Streams database. This database can be accessed using the data_store
variable which is an instance of the Datastore class. It follows the data
structure described in the type hints.

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
from typing import TypedDict


class User(TypedDict):
    u_id: str
    email: str
    password: str
    name_first: str
    name_last: str
    handle_str: str
    session_ids: list[int]


class Message(TypedDict):
    message_id: str
    u_id: int
    message: str
    time_created: int


class Channel(TypedDict):
    channel_id: int
    name: str
    owner_members: list[int]
    all_members: list[int]
    is_public: bool
    messages: list[Message]


class DM(TypedDict):
    dm_id: int
    name: str
    messages: list[Message]
    members: list[int]
    owner: int


class DatastoreType(TypedDict):
    users: list[User]
    channels: list[Channel]
    global_owners: list[int]
    max_message_id: int
    dms: list[DM]


INITIAL_OBJECT: DatastoreType = {
    "users": [],
    "channels": [],
    "global_owners": [],
    "dms": [],
    "max_message_id": -1,
}
DATA_STORE_FILE = "datastore.json"
WRITE_INTERVAL = 30


class Datastore:
    """Datastore class used to store data for Streams."""

    def __init__(self) -> None:
        if Path(DATA_STORE_FILE).is_file():
            try:
                self.__store = load(open(DATA_STORE_FILE))
            except:
                self.__store = deepcopy(INITIAL_OBJECT)
        else:
            self.__store = deepcopy(INITIAL_OBJECT)

    def get(self) -> DatastoreType:
        """Get the dictionary of the data base.

        Return Value:
            Returns datastore (dictionary)"""
        return self.__store

    def set(self, store: DatastoreType) -> None:
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
