import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.channels import channels_create_v2
from src.channel import channel_details_v2
from src import config, auth
from src.other import clear_v1


def quit_gracefully(*args):
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
    print(data["email"])
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


@APP.route("/clear/v1", methods=["DELETE"])
def clear():
    clear_v1()
    return {}


# Example
@APP.route("/echo", methods=["GET"])
def echo():
    data = request.args.get("data")
    if data == "echo":
        raise InputError(description='Cannot echo "echo"')
    return dumps({"data": data})


@APP.route("/channels/create/v2", methods=["POST"])
def create_channel_v2():
    data = request.json
    return dumps(channels_create_v2(data["token"], data["name"], data["is_public"]))


@APP.route("/channel/details/v2", methods=["GET"])
def get_channel_details():
    token = request.args.get("token")
    channel_id = request.args.get("channel_id")
    return dumps(channel_details_v2(token, channel_id))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
