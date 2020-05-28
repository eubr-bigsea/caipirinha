# -*- coding: utf-8 -*-}

import logging

from caipirinha.app_auth import requires_auth
from caipirinha.schema import *
from caipirinha.service import limonero_service
from flask import current_app, request
from flask_restful import Resource
from flask_babel import gettext

log = logging.getLogger(__name__)


class VisualizationListApi(Resource):
    """ REST API for Visualization"""

    @staticmethod
    @requires_auth
    def post():
        result, result_code = dict(
            status="ERROR", 
            message=gettext("Missing json in the request body")), 401
        if request.json is not None:
            data = request.json
            request_schema = VisualizationCreateRequestSchema()
            response_schema = VisualizationItemResponseSchema()

            params = {}
            params.update(data)

            form = request_schema.load(params)
            if form.errors:
                result, result_code = dict(
                    status="ERROR", message=gettext("Validation error"),
                    errors=form.errors), 401
            else:
                try:
                    visualization = form.data
                    vis_type = visualization.type.id
                    visualization.type = VisualizationType.query.get(vis_type)
                    if visualization.type is None:
                        raise ValueError(
                            gettext('Invalid visualization type: {}').format(vis_type))
                    db.session.add(visualization)
                    db.session.commit()
                    result, result_code = response_schema.dump(
                        visualization).data, 200
                except Exception as e:
                    log.exception('Error in POST')
                    result, result_code = dict(
                            status="ERROR",
                            message=gettext("Internal error")), 500
                    if current_app.debug:
                        result['debug_detail'] = e.message
                    db.session.rollback()

        return result, result_code

def _get_visualization(visualization, job_id, task_id):
    if visualization is not None:
        # Retrieve visualization user data from Caipirinha storage

        if visualization.data is None:
            visualization.data = '{}'
        # New code using MySQL
        data = json.loads(visualization.data)
        data['id'] = visualization.id
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
    # In case of no visualization found
    else:
        result = dict(status="ERROR", 
                message=gettext("Not Found")), 404
    return result

class VisualizationDetailApi(Resource):
    """ REST API for a single instance of class Visualization """

    @staticmethod
    @requires_auth
    def get(job_id, task_id, vis_id):
        if vis_id:
            visualization = Visualization.query.get(vis_id)
        else:
            visualization = Visualization.query.filter(
                Visualization.job_id == int(job_id),
                Visualization.task_id == str(task_id)).first()
        return _get_visualization(visualization, job_id, task_id)

    @staticmethod
    @requires_auth
    def delete(job_id, task_id, vis_id):
        result, result_code = dict(status="ERROR", message="Not found"), 404

        visualization = Visualization.query.get(vis_id)
        if visualization is not None:
            try:
                db.session.delete(visualization)
                db.session.commit()
                result, result_code = dict(status="OK", message="Deleted"), 200
            except Exception as e:
                log.exception('Error in DELETE')
                result, result_code = dict(status="ERROR",
                                           message="Internal error"), 500
                if current_app.debug:
                    result['debug_detail'] = str(e)
                db.session.rollback()
        return result, result_code

    @staticmethod
    @requires_auth
    def patch(job_id, task_id, vis_id):
        result = dict(status="ERROR", 
                    message=gettext("Insufficient data"))
        result_code = 404
        if request.json:
            data = request.json
            request_schema = partial_schema_factory(
                VisualizationCreateRequestSchema)
            # Ignore missing fields to allow partial updates
            form = request_schema.load(data, partial=True)
            response_schema = VisualizationItemResponseSchema()
            if not form.errors:
                try:
                    form.data.id = vis_id
                    visualization= db.session.merge(form.data)
                    db.session.commit()

                    if visualization is not None:
                        result, result_code = dict(
                            status="OK", message=gettext("Updated"),
                            data=response_schema.dump(visualization).data), 200
                    else:
                        result = dict(status="ERROR", 
                                message=gettext("Not found"))
                except Exception as e:
                    log.exception('Error in PATCH')
                    result, result_code = dict(
                            status="ERROR",
                            message=gettext("Internal error")), 500
                    if current_app.debug:
                        result['debug_detail'] = str(e)
                    db.session.rollback()
            else:
                result = dict(status="ERROR", 
                        message=gettext("Invalid data"),
                        errors=form.errors)
        return result, result_code

class PublicVisualizationApi(Resource):
    @staticmethod
    def get(job_id, task_id, vis_id):
        if task_id in ['0', 'undefined']:
            visualization = Visualization.query.get(vis_id)
        else:
            visualization = Visualization.query.filter(
                Visualization.job_id == int(job_id),
                Visualization.task_id == str(task_id)).first()
    
        if visualization.dashboard is not None and \
                visualization.dashboard.is_public:
            return _get_visualization(visualization, job_id, task_id)
        else:
            result, result_code = dict(
                status="ERROR", 
                message=gettext("Missing json in the request body")), 401
            return result, result_code



