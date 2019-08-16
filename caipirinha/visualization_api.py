# -*- coding: utf-8 -*-}

import logging

from caipirinha.app_auth import requires_auth
from caipirinha.schema import *
from caipirinha.service import limonero_service
from flask import current_app, request
from flask_restful import Resource

log = logging.getLogger(__name__)


class VisualizationListApi(Resource):
    """ REST API for Visualization"""

    @staticmethod
    @requires_auth
    def post():
        result, result_code = dict(
            status="ERROR", message="Missing json in the request body"), 401
        if request.data is not None:
            data = json.loads(request.data)
            request_schema = VisualizationCreateRequestSchema()
            response_schema = VisualizationItemResponseSchema()

            params = {}
            params.update(data)

            form = request_schema.load(params)
            if form.errors:
                result, result_code = dict(
                    status="ERROR", message="Validation error",
                    errors=form.errors), 401
            else:
                try:
                    visualization = form.data
                    vis_type = visualization.type.id
                    visualization.type = VisualizationType.query.get(vis_type)
                    if visualization.type is None:
                        raise ValueError(
                            'Invalid visualization type: {}'.format(vis_type))
                    db.session.add(visualization)
                    db.session.commit()
                    result, result_code = response_schema.dump(
                        visualization).data, 200
                except Exception as e:
                    log.exception('Error in POST')
                    result, result_code = dict(status="ERROR",
                                               message="Internal error"), 500
                    if current_app.debug:
                        result['debug_detail'] = e.message
                    db.session.rollback()

        return result, result_code


class VisualizationDetailApi(Resource):
    """ REST API for a single instance of class Visualization """

    @staticmethod
    @requires_auth
    def get(job_id, task_id):
        # Check the existence of such visualization
        visualization = Visualization.query.filter(
            Visualization.job_id == int(job_id),
            Visualization.task_id == str(task_id)).first()

        if visualization is not None:
            # Retrieve visualization user data from Caipirinha storage

            if visualization.data is not None:
                # New code using MySQL
                data = json.loads(visualization.data)
                if visualization.type_id == 35:  # table
                    result = dict(
                        job_id=job_id, task_id=task_id,
                        suggested_width=visualization.suggested_width,
                        type=dict(id=visualization.type_id,
                                  icon=visualization.type.icon,
                                  name=visualization.type.name),
                        title=visualization.title,
                        # labels=labels,
                        # attributes=attributes,
                        data=data)
                else:
                    result = dict(
                        job_id=job_id, task_id=task_id,
                        # suggested_width=visualization.suggested_width,
                        type=dict(id=visualization.type_id,
                                  icon=visualization.type.icon,
                                  name=visualization.type.name),
                        title=visualization.title,
                        # labels=labels,
                        # attributes=attributes,
                    )
                    result.update(data)
            else:
                result = dict(status="ERROR",
                              message="Missing visualization data"), 400
        # In case of no visualization found
        else:
            result = dict(status="ERROR", message="Not Found"), 404
        return result
