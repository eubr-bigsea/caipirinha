#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logging.config

import argparse
import eventlet
import eventlet.wsgi
import os
import sqlalchemy_utils
import yaml
from caipirinha.dashboard_api import DashboardDetailApi, DashboardListApi
from caipirinha.models import Dashboard
from flask import Flask, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import get_locale, Babel
from flask_cors import CORS
from flask_restful import Api, abort
from caipirinha.models import db

sqlalchemy_utils.i18n.get_locale = get_locale

eventlet.monkey_patch(all=True)
app = Flask(__name__)

babel = Babel(app)

logging.config.fileConfig('logging_config.ini')

app.secret_key = 'l3m0n4d1'
# Flask Admin 
admin = Admin(app, name='Lemonade', template_mode='bootstrap3')

# CORS
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

mappings = {
    '/dashboards': DashboardListApi,
    '/dashboards/<int:dashboard_id>': DashboardDetailApi,
}
for path, view in mappings.iteritems():
    api.add_resource(view, path)


# @app.before_request
def before():
    if request.args and 'lang' in request.args:
        if request.args['lang'] not in ('es', 'en'):
            return abort(404)


@babel.localeselector
def get_locale():
    return request.args.get('lang', 'en')


def main(is_main_module):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str,
            help="Config file", required=True)
    args = parser.parse_args()

    config_file = args.config

    logger = logging.getLogger(__name__)
    if config_file:
        with open(config_file) as f:
            config = yaml.load(f)['caipirinha']

        app.config["RESTFUL_JSON"] = {"cls": app.json_encoder}

        server_config = config.get('servers', {})
        app.config['SQLALCHEMY_DATABASE_URI'] = server_config.get(
            'database_url')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_SIZE'] = 10
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 240

        app.config.update(config.get('config', {}))

        db.init_app(app)

        port = int(config.get('port', 5000))
        logger.debug('Running in %s mode', config.get('environment'))

        if is_main_module:
            if config.get('environment', 'dev') == 'dev':
                admin.add_view(ModelView(Dashboard, db.session))
                app.run(debug=True, port=port)
            else:
                eventlet.wsgi.server(eventlet.listen(('', port)), app)
    else:
        logger.error('Please, set CAIPIRINHA_CONFIG environment variable')
        exit(1)


main(__name__ == '__main__')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str,
            help="Config file", required=True)
    args = parser.parse_args()

    eventlet.monkey_patch(all=True)

    from stand.factory import create_app, create_babel_i18n, \
        create_socket_io_app, create_redis_store

    app = create_app(config_file=args.config)
    babel = create_babel_i18n(app)
    # socketio, socketio_app = create_socket_io_app(app)
    stand_socket_io = StandSocketIO(app)
    redis_store = create_redis_store(app)

    if app.debug:
        app.run(debug=True)
    else:        
        port = int(app.config['STAND_CONFIG'].get('port', 5000))

        # noinspection PyUnresolvedReferences
        eventlet.wsgi.server(eventlet.listen(('', port)),
                         stand_socket_io.socket_app)