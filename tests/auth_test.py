import pytest

from src.auth import auth_login_v1, auth_register_v1
from src.data_store import data_store
from src.other import clear_v1
from src.error import InputError


def test_login():
    clear_v1()
    user_id = auth_register_v1("wow@wow.com", "awesome", "first", "last")
    assert auth_login_v1("wow@wow.com", "awesome") == user_id


def test_wrong_login():
    clear_v1()
    with pytest.raises(InputError):
        assert auth_login_v1("not@email.com", "password")


def test_invalid_register():
    clear_v1()
    # password < 6 charecters
    with pytest.raises(InputError):
        assert auth_register_v1("wow@wow.com", "no", "first", "last")
    clear_v1()

    # too short firstname
    with pytest.raises(InputError):
        assert auth_register_v1("wow@wow.com", "password", "", "last")
    clear_v1()

    # too long firstname
    with pytest.raises(InputError):
        assert auth_register_v1(
            "wow@wow.com",
            "password",
            "thisnameislongerthan50charecterslongthisnameislongerthan50charecterslong",
            "last",
        )
    clear_v1()

    # too short lastname
    with pytest.raises(InputError):
        assert auth_register_v1("wow@wow.com", "password", "first", "")
    clear_v1()

    # too long lastname
    with pytest.raises(InputError):
        assert auth_register_v1(
            "wow@wow.com",
            "password",
            "first",
            "thisnameislongerthan50charecterslongthisnameislongerthan50charecterslong",
        )
    clear_v1()

    # incorrect email
    with pytest.raises(InputError):
        assert auth_register_v1("ow.com", "password", "first", "last")


def test_existing_email():
    clear_v1()

    auth_register_v1("wow@wow.com", "password", "first", "last")
    store = data_store.get()
    print(store)
    with pytest.raises(InputError):
        assert auth_register_v1(
            "wow@wow.com", "password2", "thewfirstname", "thelastname"
        )


def test_existing_handle():
    clear_v1()

    auth_register_v1("email@email.com", "password", "first", "last")
    user_id0 = auth_register_v1("email1@email.com", "password2", "first", "last")
    user_id1 = auth_register_v1("email2@email.com", "password3", "first", "last")

    users = data_store.get()["users"]
    for user in users:
        if user["u_id"] == user_id0:
            assert user["handle_str"] == "firstlast0"
        if user["u_id"] == user_id1:
            assert user["handle_str"] == "firstlast1"


def test_multiple_register():
    clear_v1()
    auth_register_v1("email1@email.com", "password", "first", "last")
    auth_register_v1("email2@email.com", "password1", "first1", "last1")
    auth_register_v1("email3@email.com", "password2", "first2", "last2")


def test_multiple_id():
    clear_v1()
    id1 = auth_register_v1("email1@email.com", "password", "first", "last")[
        "auth_user_id"
    ]
    id2 = auth_register_v1("email2@email.com", "password1", "first1", "last1")[
        "auth_user_id"
    ]
    id3 = auth_register_v1("email3@email.com", "password2", "first2", "last2")[
        "auth_user_id"
    ]
    assert id1 != id2
    assert id2 != id3
    assert id1 != id3


def test_max_length_handle():
    clear_v1()

    auth_register_v1("email@email.com", "password", "firstverylongname", "lastname")
    user_id0 = auth_register_v1(
        "email1@email.com", "password2", "firstverylongname", "lastname"
    )
    user_id1 = auth_register_v1(
        "email2@email.com", "password3", "firstverylongname", "lastname"
    )

    users = data_store.get()["users"]
    for user in users:
        if user["u_id"] == user_id0:
            assert user["handle_str"] == "firstverylongnamelas0"
        if user["u_id"] == user_id1:
            assert user["handle_str"] == "firstverylongnamelas1"