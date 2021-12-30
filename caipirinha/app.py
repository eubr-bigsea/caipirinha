#!/usr/bin/env python
# -*- coding: utf-8 -*-
# noinspection PyBroadException
try:
    import eventlet
    eventlet.monkey_patch(all=True)
except:
    pass

import logging
import logging.config
import eventlet.wsgi
import os
import sqlalchemy_utils
import yaml
from flask import json

from caipirinha.dashboard_api import DashboardDetailApi, DashboardListApi
from caipirinha.public_dashboard_api import PublicDashboardApi
from caipirinha.models import db
from flask import Flask, request, g as flask_g
from flask_swagger_ui import get_swaggerui_blueprint
from flask_babel import get_locale, Babel
from flask_cors import CORS
from flask_restful import Api, abort
from flask_migrate import Migrate
from caipirinha.visualization_api import (VisualizationDetailApi,
    VisualizationListApi, PublicVisualizationApi)
from caipirinha.text_api import TextListApi, TextDetailApi

from sqlalchemy import exc
from sqlalchemy import event
from sqlalchemy.pool import Pool

@ event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor=dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        raise exc.DisconnectionError()
    cursor.close()


def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response=e.get_response()
    # replace the body with JSON
    response.data=json.dumps({
        "status": "ERROR",
        "code": e.code,
        "name": e.name,
        "message": e.description,
    })
    response.content_type="application/json"
    return response

def create_app(main_module=False):
    app=Flask(__name__,
         static_url_path = '/static',
         static_folder = 'static')

    babel=Babel(app)

    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.abspath(
        'caipirinha/i18n/locales')
    logging.config.fileConfig('logging_config.ini')

    app.secret_key='l3m0n4d1'

    # CORS
    CORS(app, resources = {r"/*": {"origins": "*"}})

    # Swagger
    swaggerui_blueprint=get_swaggerui_blueprint(
        '/api/docs',  
        '/static/swagger.yaml',
        config={  # Swagger UI config overrides
            'app_name': "Lemonade Caipirinha"
        },
        # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
        #    'clientId': "your-client-id",
        #    'clientSecret': "your-client-secret-if-required",
        #    'realm': "your-realms",
        #    'appName': "your-app-name",
        #    'scopeSeparator': " ",
        #    'additionalQueryStringParams': {'test': "hello"}
        # }
    )
    
    app.register_blueprint(swaggerui_blueprint)
    
    # Error handling
    app.register_error_handler(404, handle_exception)

    # API
    api = Api(app)
    
    mappings = {
        '/dashboards': [DashboardListApi, 'dashboardList'],
        '/public/dashboard/<h>': [PublicDashboardApi, 'publicDashboard'],
        '/dashboards/<int:dashboard_id>': [DashboardDetailApi, 'dashboardDetail'],
        '/visualizations/<int:job_id>/<task_id>/<int:vis_id>': [
            VisualizationDetailApi, 'visualizationDetail'],
        '/visualizations/<int:job_id>/<task_id>': [
            VisualizationDetailApi, 'visualizationDetailOld'],
        '/visualizations/<int:job_id>/<task_id>': [
            VisualizationDetailApi, 'visualizationDetailOld'],
        '/public/visualization/<int:job_id>/<task_id>/<int:vis_id>': [
            PublicVisualizationApi, 'publicVisualization'],
        '/visualizations': [VisualizationListApi, 'visualizationList'],
        '/texts': [TextListApi, 'textList'],
        '/texts/<int:text_id>': [TextDetailApi, 'textDetail'],
    }
    for path, view in list(mappings.items()):
        api.add_resource(view[0], path, endpoint=view[1])
    

    config_file = os.environ.get('CAIPIRINHA_CONFIG')

    os.chdir(os.environ.get('CAIPIRINHA_HOME', '.'))
    logger = logging.getLogger(__name__)

    migrate = Migrate(app, db)

    @babel.localeselector
    def get_locale():
        user = getattr(flask_g, 'user', None)
        if user is not None and user.locale:
            return user.locale
        else:
            return request.args.get(
                'lang', request.accept_languages.best_match(['en', 'pt', 'es']))

    sqlalchemy_utils.i18n.get_locale = get_locale
    
    if config_file:
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)['caipirinha']

        app.config["RESTFUL_JSON"] = {"cls": app.json_encoder}

        server_config = config.get('servers', {})
        app.config['SQLALCHEMY_DATABASE_URI'] = server_config.get(
            'database_url')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        engine_config = config.get('config', {})
        if engine_config:
            final_config = {'pool_pre_ping': True}
            if 'mysql://' in app.config['SQLALCHEMY_DATABASE_URI']:
                if 'SQLALCHEMY_POOL_SIZE' in engine_config: 
                    final_config['pool_size'] = engine_config['SQLALCHEMY_POOL_SIZE'] 
                if 'SQLALCHEMY_POOL_RECYCLE' in engine_config: 
                    final_config['pool_recycle'] = engine_config['SQLALCHEMY_POOL_RECYCLE']
            app.config['SQLALCHEMY_ENGINE_OPTIONS'] = final_config

        app.config['CAIPIRINHA_CONFIG'] = config

        db.init_app(app)

        port = int(config.get('port', 5000))
        logger.debug('Running in %s mode', config.get('environment'))

        if main_module:
            if config.get('environment', 'dev') == 'dev':
                app.run(debug=True, port=port)
            else:
                eventlet.wsgi.server(eventlet.listen(('', port)), app)
        else:
            return app
    else:
        logger.error('Please, set CAIPIRINHA_CONFIG environment variable')
        exit(1)

if __name__ == '__main__':
    create_app(True)
