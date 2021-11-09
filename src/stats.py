import re
from src.data_store import data_store
from src.error import InputError
from src.auth import extract_token


def user_stats(token):
    """Calculates the user's involvement rate and returns their stats

    Arguments:
        token (str) - An encoded JWT token

    Exceptions:
        AccessError - Invalid token

    Return Value:
        Returns { channels_joined, dms_joined, messages_sent, involvement_rate }
    """
    # Validates the given token
    token_data = extract_token(token)

    # Fetching the data_store
    store = data_store.get()
    workspace = store["workspace_stats"]
    users = store["users"]

    # Finding the given user
    found_user = [user for user in users if token_data["u_id"] == user["u_id"]][0]

    # Finds the total number of channels, dms, and messages
    total_channels = workspace["channels_exist"][-1]["num_channels_exist"]
    total_dms = workspace["dms_exist"][-1]["num_dms_exist"]
    total_messages = workspace["messages_exist"][-1]["num_messages_exist"]

    # Finding the number of channels, dms, and messages related to the user
    user_stats = found_user["user_stats"]
    user_channels = user_stats["channels_joined"][-1]["num_channels_joined"]
    user_dms = user_stats["dms_joined"][-1]["num_dms_joined"]
    user_messages = user_stats["messages_sent"][-1]["num_messages_sent"]

    # Calculating the involvement rate
    sum_total = total_channels + total_dms + total_messages
    sum_user = user_channels + user_dms + user_messages
    try:
        involvement_rate = sum_user / sum_total
    except:
        involvement_rate = 0

    # Returns the user stats structure
    return {
        "channels_joined": user_stats["channels_joined"],
        "dms_joined": user_stats["dms_joined"],
        "messages_sent": user_stats["messages_sent"],
        "involvement_rate": involvement_rate,
    }


def workspace_stats(token):
    """Calculates the workspace's utilization rate and returns the stats for
    the entire workspace

    Arguments:
        token (str) - An encoded JWT token

    Exceptions:
        AccessError - Invalid token

    Return Value:
        Returns { num_channels, num_dms, messages_sent, utilization_rate }
    """
    # Validates the given token
    token_data = extract_token(token)

    # Fetching the data_store
    store = data_store.get()
    workspace = store["workspace_stats"]
    users = store["users"]

    # Calculating the number of users that have joined at least one channel
    sum_users = 0
    for user in users:
        if user["user_stats"]["channels_joined"][-1]["num_channels_joined"] != 0:
            sum_users += 1
        elif user["user_stats"]["dms_joined"][-1]["num_dms_joined"] != 0:
            sum_users += 1

    # Calculating the total number of users
    total_users = len(users)

    # Calculating the utilization rate
    try:
        utilization_rate = sum_users / total_users
    except:
        utilization_rate = 0

    # Returning the workspace stats structure
    return {
        "channels_exist": workspace["channels_exist"],
        "dms_exist": workspace["dms_exist"],
        "messages_exist": workspace["messages_exist"],
        "utilization_rate": utilization_rate,
    }
