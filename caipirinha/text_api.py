# -*- coding: utf-8 -*-}

import logging

from caipirinha.app_auth import requires_auth
from caipirinha.schema import *
from flask import current_app, request
from flask_restful import Resource

log = logging.getLogger(__name__)
MARKDOWN_ID=72

class TextListApi(Resource):
    """ REST API for Text"""

    @staticmethod
    @requires_auth
    def post():
        result, result_code = dict(
            status="ERROR", message="Missing json in the request body"), 400
        if request.json is not None:
            data = request.json
            request_schema = VisualizationCreateRequestSchema()
            response_schema = VisualizationItemResponseSchema()

            params = {'title': '', 'type': {'id': MARKDOWN_ID}}
            params.update(data)

            form = request_schema.load(params)
            dashboard_id = request.json.get('dashboard', {}).get('id')

            if form.errors or dashboard_id is None:
                result, result_code = dict(
                    status="ERROR", message="Validation error",
                    errors=form.errors), 400
            else:
                try:
                    visualization = form.data
                    visualization.title = '' if visualization.title is None \
                            else visualization.title
                    visualization.type = VisualizationType.query.get(MARKDOWN_ID)
                    visualization.dashboard = Dashboard.query.get(dashboard_id)

                    db.session.add(visualization)
                    db.session.commit()
                    result, result_code = response_schema.dump(
                        visualization).data, 200
                except Exception as e:
                    log.exception('Error in POST')
                    result, result_code = dict(status="ERROR",
                                               message="Internal error"), 500
                    if current_app.debug:
                        result['debug_detail'] = str(e)
                    db.session.rollback()

        return result, result_code

class TextDetailApi(Resource):
    """ REST API for a single instance of class Text """

    @staticmethod
    @requires_auth
    def get(job_id, task_id):
        # Check the existence of such visualization
        visualization = Text.query.filter(
            Text.job_id == int(job_id),
            Text.task_id == str(task_id)).first()
        return _get_visualization(visualization, job_id, task_id)


