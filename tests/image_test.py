from src.error import InputError, AccessError
import requests
from src.config import url


def test_image():
    requests.delete(url + "clear/v1")

    r = requests.post(f"{url}auth/register/v2", json={})
