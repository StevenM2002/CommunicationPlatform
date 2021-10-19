import signal
from json import dumps
from flask import Flask
from flask_cors import CORS
from src import config
from src.channels import channels_create_v2


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
    data = request.get_json()
    return dumps(channels_create_v2(data["token"], data["name"], data["is_public"]))


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
