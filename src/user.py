import re
import urllib.request
from PIL import Image
from src.data_store import data_store, IMAGE_FOLDER
from src.error import InputError
from src.auth import extract_token
from src.config import url


def all_users(token):
    """Returns a list of all users when given a valid token

    Arguments:
        token (str) - an encoded JWT token

    Exceptions:
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns users list upon completion

    """
    # Loading the data store
    store = data_store.get()

    # Validating the input token
    extract_token(token)

    # Returning the list of users
    users = [
        {
            "u_id": user["u_id"],
            "email": user["email"],
            "name_first": user["name_first"],
            "name_last": user["name_last"],
            "handle_str": user["handle_str"],
            "profile_img_url": user["profile_img_url"],
        }
        for user in store["users"]
    ]
    return {"users": users}


def user_profile(token, u_id):
    """Returns a user's information when given a channel_id

    Arguments:
        token (str) - an encoded JWT token
        u_id (int) - the id of the required user

    Exceptions:
        InputError - Occurs when u_id does not refer to a valid user
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns {name_first, name_last, email, handle_str}

    """
    # Loading the data store
    store = data_store.get()
    users = store["users"]
    removed = store["removed_users"]
    u_id = int(u_id)
    # Validating the input token
    extract_token(token)

    # Finding the correct user
    found_user = [user for user in users if user["u_id"] == u_id]

    # Check to ensure a valid user has been found
    if len(found_user) == 0:
        found_user = [user for user in removed if user["u_id"] == u_id]

    if len(found_user) == 0:
        raise InputError(description="User Not Found")

    user = {
        key: value
        for key, value in found_user[0].items()
        if key not in ("session_ids", "password", "user_stats", "reset_codes")
    }
    return {"user": user}


def user_set_name(token, name_first, name_last):
    """Returns a list of all users when given a valid token

    Arguments:
        token (str) - an encoded JWT token
        name_first (str) - user's new first name
        name_last (str) - user's new last name

    Exceptions:
        InputError - Occurs when:
            Length of name_first or name_last is not within 1 to 50 characters
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns {}
    """
    # Loading the data store
    store = data_store.get()
    users = store["users"]

    # Validating the token
    u_information = extract_token(token)

    # Checks the length of the given strings, returning input errors if not
    for name in (name_first, name_last):
        if len(name) < 1 or len(name) > 50:
            raise InputError(description="Invalid Length of Name")

    # Changes the values in the dictionary
    found_user = [user for user in users if user["u_id"] == u_information["u_id"]][0]
    found_user["name_first"] = name_first
    found_user["name_last"] = name_last

    return {}


def user_set_email(token, email):
    """Returns a list of all users when given a valid token

    Arguments:
        token (str) - an encoded JWT token
        email (str) - user's new email

    Exceptions:
        InputError - Occurs when:
            Email is not the valid regular expression
            Email address is already being used by another user
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns {}

    """
    # Loading the data store
    store = data_store.get()
    users = store["users"]

    # Validating the token
    u_information = extract_token(token)

    # Checks if the given email fits the correct regex
    if not re.fullmatch(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$", email):
        raise InputError(description="invalid email")

    # Checks if the email address is being used
    invalid = any(True for user in users if user["email"] == email)
    if invalid:
        raise InputError(description="Email already in use")

    # Changes the values in the dictionary
    found_user = [user for user in users if user["u_id"] == u_information["u_id"]][0]
    found_user["email"] = email
    return {}


def user_set_handle(token, handle_str):
    """Returns a list of all users when given a valid token

    Arguments:
        token (str) - an encoded JWT token
        handle (str)

    Exceptions:
        InputError - Occurs when:
            Length of handle is not within 3 to 20 characters
            handle_str contains non-alphanumeric characters
            The handle is already in use by another user
        AccessError - Occurs when the token is invalid

    Return Value:
        Returns {}

    """
    # Loading the data store
    store = data_store.get()
    users = store["users"]

    # Validating the token
    u_information = extract_token(token)

    # Checking that the length of the handle is valid
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description="Handle is of invalid length")

    # Checking that handle only has alphanumeric
    if not handle_str.isalnum():
        raise InputError(description="Handle contains non alphanumeric characters")

    # Checks if the handle is being used
    invalid = any(True for user in users if user["handle_str"] == handle_str)
    if invalid:
        raise InputError(description="Handle already in use")

    # Changes the values in the dictionary
    found_user = [user for user in users if user["u_id"] == u_information["u_id"]][0]
    found_user["handle_str"] = handle_str
    return {}


def user_upload_photo(token, img_url, x_start, y_start, x_end, y_end):
    """Given a URL of an image on the internet, crops the image within bounds

    Arguments:
        token (str) - an encoded JWT token
        img_url (str) - url to image
        x_start (int) - pixel to start crop x
        y_start (int) - pixel to start crop y
        x_end (int) - pixel to end crop x
        y_end (int) - pixel to end crop y

    Exceptions:
        InputError - Occurs when:
            - img_url returns an HTTP status other than 200
            - any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
            - x_end is less than x_start or y_end is less than y_start
            - image uploaded is not a JPG

    Return Value:
        Returns {}

    """
    u_information = extract_token(token)
    store = data_store.get()
    users = store["users"]

    # fetch image
    img_file = f"{IMAGE_FOLDER}/{u_information['u_id']}img.jpg"
    try:
        urllib.request.urlretrieve(img_url, img_file)
    except:
        raise InputError

    # crop image

    imageObject = Image.open(img_file)
    try:
        cropped = imageObject.crop((x_start, y_start, x_end, y_end))
    except:
        raise InputError
    cropped.save(img_file)

    # serve image
    for user in users:
        if user["u_id"] == u_information["u_id"]:
            user[
                "profile_img_url"
            ] = f"{url}imgfolder/{str(u_information['u_id'])}img.jpg"

    data_store.set(store)
