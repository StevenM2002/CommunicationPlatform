from copy import deepcopy
from src.data_store import data_store, INITIAL_OBJECT


def clear_v1():
    data_store.set(deepcopy(INITIAL_OBJECT))
