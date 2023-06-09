import signal
from json import dumps
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
from src.admin import admin_user_permission_change_v1, admin_user_remove_v1
from src import config, auth, dm, message
from src.channel import (
    channel_details_v2,
    channel_invite_v2,
    channel_join_v2,
    channel_addowner_v1,
    channel_leave_v1,
    channel_removeowner_v1,
)
from src.channels import (
    channels_create_v2,
    channels_listall_v2,
    channels_list_v2,
)
from src.data_store import clear_v1, IMAGE_FOLDER
from src.error import InputError
from src.auth import extract_token
from src.user import (
    all_users,
    user_profile,
    user_set_name,
    user_set_email,
    user_set_handle,
    user_upload_photo,
)
from src.stats import user_stats, workspace_stats
from src.search import search_v1
from src.notifications import notifications_get_v1

from flask import Flask, request, send_from_directory
from flask_cors import CORS


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


APP = Flask(__name__, static_url_path="")
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


@APP.route("/auth/passwordreset/request/v1", methods=["POST"])
def auth_password_reset_request():
    data = request.json
    auth.auth_password_reset_request_v1(data["email"])
    return {}


@APP.route("/auth/passwordreset/reset/v1", methods=["POST"])
def auth_password_reset():
    data = request.json
    auth.auth_password_reset_v1(data["reset_code"], data["new_password"])
    return {}


@APP.route("/dm/create/v1", methods=["POST"])
def dm_create():
    data = request.json
    return dumps(dm.dm_create_v1(data["token"], data["u_ids"]))


@APP.route("/dm/list/v1", methods=["GET"])
def dm_list():
    token = request.args.get("token")
    return dumps(dm.dm_list_v1(token))


@APP.route("/dm/remove/v1", methods=["DELETE"])
def dm_remove():
    data = request.json
    return dumps(dm.dm_remove_v1(data["token"], data["dm_id"]))


@APP.route("/dm/details/v1", methods=["GET"])
def dm_details():
    token = request.args.get("token")
    dm_id = int(request.args.get("dm_id"))
    return dumps(dm.dm_details_v1(token, dm_id))


@APP.route("/dm/leave/v1", methods=["POST"])
def dm_leave():
    data = request.json
    return dumps(dm.dm_leave_v1(data["token"], data["dm_id"]))


@APP.route("/dm/messages/v1", methods=["GET"])
def dm_messages():
    token = request.args.get("token")
    dm_id = int(request.args.get("dm_id"))
    start = int(request.args.get("start"))
    return dumps(dm.dm_messages_v1(token, dm_id, start))


@APP.route("/clear/v1", methods=["DELETE"])
def clear():
    clear_v1()
    return {}


@APP.route("/channels/listall/v2", methods=["GET"])
def channels_listingall():
    token = request.args.get("token")
    return dumps(channels_listall_v2(token))


@APP.route("/channels/list/v2", methods=["GET"])
def channels_listing():
    token = request.args.get("token")
    return dumps(channels_list_v2(token))


@APP.route("/channel/addowner/v1", methods=["POST"])
def channel_addingowner():
    data = request.get_json()
    return dumps(channel_addowner_v1(data["token"], data["channel_id"], data["u_id"]))


@APP.route("/channel/removeowner/v1", methods=["POST"])
def channel_removingowner():
    data = request.get_json()
    return dumps(
        channel_removeowner_v1(data["token"], data["channel_id"], data["u_id"])
    )


@APP.route("/channels/create/v2", methods=["POST"])
def create_channel_v2():
    data = request.json
    return dumps(channels_create_v2(data["token"], data["name"], data["is_public"]))


@APP.route("/channel/details/v2", methods=["GET"])
def get_channel_details():
    token = request.args.get("token")
    channel_id = request.args.get("channel_id")
    return dumps(channel_details_v2(token, channel_id))


@APP.route("/users/all/v1", methods=["GET"])
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
    return dumps(user_set_handle(data["token"], data["handle_str"]))


@APP.route("/user/profile/uploadphoto/v1", methods=["POST"])
def upload_photo():
    data = request.json
    return dumps(
        user_upload_photo(
            data["token"],
            data["img_url"],
            data["x_start"],
            data["y_start"],
            data["x_end"],
            data["y_end"],
        )
    )


@APP.route("/imgfolder/<path:path>")
def serve_image(path):
    return send_from_directory("../imgfolder", path)


@APP.route("/channel/invite/v2", methods=["POST"])
def do_channel_invite():
    params = request.get_json()
    token = params["token"]
    channel_id = params["channel_id"]
    u_id = params["u_id"]
    return dumps(channel_invite_v2(token, channel_id, u_id))


@APP.route("/channel/join/v2", methods=["POST"])
def do_channel_join():
    params = request.get_json()
    token = params["token"]
    channel_id = params["channel_id"]
    return dumps(channel_join_v2(token, channel_id))


@APP.route("/channel/leave/v1", methods=["POST"])
def leave_channel():
    data = request.get_json()
    return dumps(channel_leave_v1(data["token"], data["channel_id"]))


@APP.route("/channel/messages/v2", methods=["GET"])
def get_messages():
    user_id = extract_token(request.args.get("token"))["u_id"]
    channel_id = request.args.get("channel_id")
    start = request.args.get("start")
    if not channel_id.isnumeric() or not start.isnumeric():
        raise InputError(description="channel_id and start must be integers")
    return dumps(message.channel_messages_v1(user_id, int(channel_id), int(start)))


@APP.route("/message/send/v1", methods=["POST"])
def send_message():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(message.message_send_v1(user_id, data["channel_id"], data["message"]))


@APP.route("/message/edit/v1", methods=["PUT"])
def edit_message():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(message.message_edit_v1(user_id, data["message_id"], data["message"]))


@APP.route("/message/senddm/v1", methods=["POST"])
def send_dm():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(message.message_senddm_v1(user_id, data["dm_id"], data["message"]))


@APP.route("/message/remove/v1", methods=["DELETE"])
def remove_message():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(message.message_remove_v1(user_id, data["message_id"]))


@APP.route("/message/react/v1", methods=["POST"])
def react_message():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(
        message.message_react_v1(user_id, data["message_id"], data["react_id"])
    )


@APP.route("/message/unreact/v1", methods=["POST"])
def unreact_message():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(
        message.message_unreact_v1(user_id, data["message_id"], data["react_id"])
    )


@APP.route("/message/pin/v1", methods=["POST"])
def pin_message():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(message.message_pin_v1(user_id, data["message_id"]))


@APP.route("/message/unpin/v1", methods=["POST"])
def unpin_message():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(message.message_unpin_v1(user_id, data["message_id"]))


@APP.route("/message/share/v1", methods=["POST"])
def share_message():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(
        message.message_share_v1(
            user_id,
            data["og_message_id"],
            data["message"],
            data["channel_id"],
            data["dm_id"],
        )
    )


@APP.route("/message/sendlater/v1", methods=["POST"])
def message_sendlater():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(
        message.message_sendlater(
            user_id, data["channel_id"], data["message"], data["time_sent"]
        )
    )


@APP.route("/message/sendlaterdm/v1", methods=["POST"])
def dm_sendlater():
    data = request.json
    user_id = extract_token(data["token"])["u_id"]
    return dumps(
        message.message_sendlater_dm(
            user_id, data["dm_id"], data["message"], data["time_sent"]
        )
    )


@APP.route("/admin/user/remove/v1", methods=["DELETE"])
def do_admin_user_remove():
    params = request.get_json()
    u_id = params["u_id"]
    token = params["token"]
    return dumps(admin_user_remove_v1(token, u_id))


@APP.route("/admin/userpermission/change/v1", methods=["POST"])
def do_admin_userpermission_change():
    params = request.get_json()
    token = params["token"]
    u_id = params["u_id"]
    permission_id = params["permission_id"]
    return dumps(admin_user_permission_change_v1(token, u_id, permission_id))


@APP.route("/search/v1", methods=["GET"])
def search_the_messages():
    token = request.args.get("token")
    query_str = request.args.get("query_str")
    return dumps(search_v1(token, query_str))


@APP.route("/notifications/get/v1", methods=["GET"])
def get_notifications():
    token = request.args.get("token")
    u_id = extract_token(token)["u_id"]
    return dumps(notifications_get_v1(u_id))


@APP.route("/standup/start/v1", methods=["POST"])
def do_standup_start():
    params = request.get_json()
    return dumps(
        standup_start_v1(params["token"], params["channel_id"], params["length"])
    )


@APP.route("/standup/active/v1", methods=["GET"])
def do_standup_active():
    token = request.args.get("token")
    channel_id = int(request.args.get("channel_id"))
    return dumps(standup_active_v1(token, channel_id))


@APP.route("/standup/send/v1", methods=["POST"])
def do_standup_send():
    params = request.get_json()
    return dumps(
        standup_send_v1(params["token"], params["channel_id"], params["message"])
    )


@APP.route("/user/stats/v1", methods=["GET"])
def do_user_stats():
    data = request.args.get("token")
    return dumps(user_stats(data))


@APP.route("/users/stats/v1", methods=["GET"])
def do_workspace_stats():
    data = request.args.get("token")
    return dumps(workspace_stats(data))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
