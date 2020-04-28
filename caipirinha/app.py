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
from caipirinha.dashboard_api import DashboardDetailApi, DashboardListApi, \
        PublicDashboardApi
from caipirinha.models import Dashboard, db
from flask import Flask, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import get_locale, Babel
from flask_cors import CORS
from flask_restful import Api, abort
from caipirinha.visualization_api import VisualizationDetailApi, \
    VisualizationListApi, PublicVisualizationApi
from caipirinha.text_api import TextListApi, TextDetailApi
sqlalchemy_utils.i18n.get_locale = get_locale

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


# @app.before_request
def before():
    if request.args and 'lang' in request.args:
        if request.args['lang'] not in ('es', 'en'):
            return abort(404)


@babel.localeselector
def get_locale():
    return request.args.get('lang', 'en')


def main(is_main_module):
    config_file = os.environ.get('CAIPIRINHA_CONFIG')

    os.chdir(os.environ.get('CAIPIRINHA_HOME', '.'))
    logger = logging.getLogger(__name__)
    if config_file:
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)['caipirinha']

        app.config["RESTFUL_JSON"] = {"cls": app.json_encoder}

        server_config = config.get('servers', {})
        app.config['SQLALCHEMY_DATABASE_URI'] = server_config.get(
            'database_url')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_POOL_SIZE'] = 10
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 240

        app.config.update(config.get('config', {}))
        app.config['CAIPIRINHA_CONFIG'] = config

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
