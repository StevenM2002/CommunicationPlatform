from src.other import clear_v1
from src.data_store import data_store


def test_users():
    data = data_store.get()
    data["users"].append({"name": "james"})
    data_store.set(data)
    clear_v1()
    data = data_store.get()
    assert len(data["channels"]) == 0
    assert len(data["users"]) == 0
    assert len(data) == 2


def test_channels():
    data = data_store.get()
    data["channels"].append({"id": 42})
    data_store.set(data)
    clear_v1()
    data = data_store.get()
    assert len(data["channels"]) == 0
    assert len(data["users"]) == 0
    assert len(data) == 2


def test_channels_and_users():
    data = data_store.get()
    data["channels"].append({"id": 42})
    data["users"].append({"name": "james"})
    data_store.set(data)
    clear_v1()
    data = data_store.get()
    assert len(data["channels"]) == 0
    assert len(data["users"]) == 0
    assert len(data) == 2


def test_other_key():
    data = data_store.get()
    data["random"] = 2
    data_store.set(data)
    clear_v1()
    data = data_store.get()
    assert len(data["channels"]) == 0
    assert len(data["users"]) == 0
    assert len(data) == 2
