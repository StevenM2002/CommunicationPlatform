import math
import time

from src import config
from src.error import AccessError, InputError

import pytest
import requests


OK = 200
INPUT_ERROR = 400
ACCESS_ERROR = 403


@pytest.fixture
def new_time():
    # Clears the Data Store and finds the timestamp of when the code was cleared
    timestamp = math.floor(time.time())
    requests.delete(f"{config.url}/clear/v1")
    return timestamp


""" ======= Workplace Stats Tests ======="""
# Tests that the initialised values for workplace stats returns the correct value


# Tests that a set of added channels, dms, and messages results in the correct stats


""" ======= User Stats Tests ======="""
# Tests that a new created user returns the correct involvement


# Tests that a user added into channels, and sending messages and dms has the
# correctly calculated engagement value
