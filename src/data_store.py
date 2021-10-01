from copy import deepcopy

INITIAL_OBJECT = {"users": [], "channels": []}


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


global data_store
data_store = Datastore()
