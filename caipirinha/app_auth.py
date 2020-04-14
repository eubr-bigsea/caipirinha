# -*- coding: utf-8 -*-}
import json
import logging
import re
from collections import namedtuple
from functools import wraps

import requests
from flask import request, Response, current_app, g as flask_g

User = namedtuple(
    "User", "id, login, email, name, first_name, last_name, locale, permissions")

MSG1 = 'Could not verify your access level for that URL. ' \
       'You have to login with proper credentials provided by Lemonade Thorn'

MSG2 = 'Could not verify your access level for that URL. ' \
       'Invalid authentication token'

CONFIG_KEY = 'CAIPIRINHA_CONFIG'

log = logging.getLogger(__name__)


def authenticate(msg, params):
    """Sends a 403 response that enables basic auth"""
    return Response(json.dumps({'status': 'ERROR', 'message': msg}), 401,
                    mimetype="application/json")

def requires_auth(f):
    @wraps(f)
    def decorated(*_args, **kwargs):
        config = current_app.config[CONFIG_KEY]
        user_id = request.headers.get('x-user-id')
        permissions = request.headers.get('x-permissions')
        user_data = request.headers.get('x-user-data')

        if all([user_data, user_id, permissions]):
            login, email, name, locale = user_data.split(';')
            setattr(flask_g, 'user', User(user_id, login, email, name, locale, '', '',
                permissions.split(',')))
            return f(*_args, **kwargs)
        else:
            return authenticate(MSG1, {'message': 'Invalid authentication'})

    return decorated



