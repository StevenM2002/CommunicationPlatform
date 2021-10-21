import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.channels import channels_create_v2
from src.channel import channel_details_v2
from src import config, auth, dm
from src.other import clear_v1
from src.error import InputError, AccessError
from src.user import (
    all_users,
    user_profile,
    user_set_name,
    user_set_email,
    user_set_handle,
)
import jwt
from src.channel import channel_invite_v1, channel_join_v1
from src.auth import JWT_SECRET

# from src.admin import admin_user_permission_change_v1, admin_user_remove_v1


def quit_gracefully(*_):
    """For coverage"""
    exit(0)


def defaultHandler(err):
    response = err.get_response()
    print("response", err, err.get_response())
    response.data = dumps(
        {
            "code": err.code,
            "name": "System Error",
            "message": err.get_description(),
        }
    )
    response.content_type = "application/json"
    return response


APP = Flask(__name__)
CORS(APP)

APP.config["TRAP_HTTP_EXCEPTIONS"] = True
APP.register_error_handler(Exception, defaultHandler)


@APP.route("/auth/login/v2", methods=["POST"])
def auth_login():
    data = request.json
    return dumps(auth.auth_login_v2(data["email"], data["password"]))


@APP.route("/auth/register/v2", methods=["POST"])
def auth_register():
    data = request.json
    return dumps(
        auth.auth_register_v2(
            data["email"], data["password"], data["name_first"], data["name_last"]
        )
    )


@APP.route("/auth/logout/v1", methods=["POST"])
def auth_logout():
    data = request.json
    auth.auth_logout_v1(data["token"])
    return {}


@APP.route("/dm/create/v1", methods=["POST"])
def dm_create():
    data = request.json
    return dumps(dm.dm_create_v1(data["token"], data["u_ids"]))


@APP.route("/dm/list/v1", methods=["GET"])
def dm_list():
    data = request.json
    return dumps(dm.dm_list_v1(data["token"]))


@APP.route("/dm/remove/v1", methods=["DELETE"])
def dm_remove():
    data = request.json
    return dumps(dm.dm_remove_v1(data["token"], data["dm_id"]))


@APP.route("/dm/details/v1", methods=["GET"])
def dm_details():
    data = request.json
    return dumps(dm.dm_details_v1(data["token"], data["dm_id"]))


@APP.route("/dm/leave/v1", methods=["POST"])
def dm_leave():
    data = request.json
    return dumps(dm.dm_leave_v1(data["token"], data["dm_id"]))


@APP.route("/dm/messages/v1", methods=["GET"])
def dm_messages():
    data = request.json
    return dumps(dm.dm_messages_v1(data["token"], data["dm_id"], data["start"]))


@APP.route("/clear/v1", methods=["DELETE"])
def clear():
    clear_v1()
    return {}


@APP.route("/channels/create/v2", methods=["POST"])
def create_channel_v2():
    data = request.json
    return dumps(channels_create_v2(data["token"], data["name"], data["is_public"]))


@APP.route("/channel/details/v2", methods=["GET"])
def get_channel_details():
    token = request.args.get("token")
    channel_id = request.args.get("channel_id")
    return dumps(channel_details_v2(token, channel_id))


@APP.route("/user/all/v1", methods=["GET"])
def get_all_users():
    token = request.args.get("token")
    return dumps(all_users(token))


@APP.route("/user/profile/v1", methods=["GET"])
def find_user():
    token = request.args.get("token")
    u_id = request.args.get("u_id")
    return dumps(user_profile(token, u_id))


@APP.route("/user/profile/setname/v1", methods=["PUT"])
def set_name():
    data = request.json
    return dumps(user_set_name(data["token"], data["name_first"], data["name_last"]))


@APP.route("/user/profile/setemail/v1", methods=["PUT"])
def set_email():
    data = request.json
    return dumps(user_set_email(data["token"], data["email"]))


@APP.route("/user/profile/sethandle/v1", methods=["PUT"])
def set_handle():
    data = request.json
    print(data)
    return dumps(user_set_handle(data["token"], data["handle_str"]))


@APP.route("/channel/invite/v2", methods=["POST"])
def channel_invite_v2():
    params = request.get_json()
    token = params["token"]
    channel_id = params["channel_id"]
    u_id = params["u_id"]
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    auth_id = decoded_token["u_id"]
    return dumps(channel_invite_v1(auth_id, channel_id, u_id))


@APP.route("/channel/join/v2", methods=["POST"])
def channel_join_v2():
    params = request.get_json()
    token = params["token"]
    channel_id = params["channel_id"]
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    auth_id = decoded_token["u_id"]
    return dumps(channel_join_v1(auth_id, channel_id))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
