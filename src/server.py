import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.channels import channels_listall_v1, channels_list_v1
from src import config, auth, dm
from src.other import clear_v1

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

@APP.route("/channels/listall/v2", methods=["GET"])
def channels_listall_v2():
    # Need to do auth the token and recieve a token?
    token = request.args.get("data")
    return dumps(channels_listall_v2(token))
    
@APP.route("/channels/list/v2", methods=["GET"])
def channels_list_v2():
    # Take out auth id from token and pass into list function
    #x = request.get_json() to get token
    token = request.args.get("data")
    return dumps(channels_list_v2(token))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
