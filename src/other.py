from copy import deepcopy
from src.data_store import data_store, initial_object


def clear_v1():
    data_store.set(deepcopy(initial_object))