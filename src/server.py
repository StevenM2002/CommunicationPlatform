import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config
from src.channel import channel_invite_v1, channel_join_v1
import jwt
from src.admin import admin_user_remove_v1, admin_user_permission_change_v1
from src.auth import JWT_SECRET
def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route('/channel/invite/v2', methods=['POST'])
def channel_invite_v2():
    params = request.get_json()
    token = params['token']
    channel_id = params['channel_id']
    u_id = params['u_id']
    decoded_token = jwt.decode(token, JWT_SECRET, algorithm='HS256')
    auth_id = decoded_token['u_id']
    return dumps(channel_invite_v1(auth_id, channel_id, u_id))

@APP.route('/channel/join/v2', methods=['POST'])
def channel_join_v2():
    params = request.get_json()
    token = params['token']
    channel_id = params['channel_id']
    decoded_token = jwt.decode(token, JWT_SECRET, algorithm='HS256')
    auth_id = decoded_token['u_id']
    return dumps(channel_join_v1(auth_id, channel_id))

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully) # For coverage
    APP.run(port=config.port) # Do not edit this port
