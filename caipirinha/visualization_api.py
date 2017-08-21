# -*- coding: utf-8 -*-}

import logging
import urlparse

import happybase
from app_auth import requires_auth
from caipirinha.service import limonero_service
from flask import current_app, request
from flask_restful import Resource
from schema import *

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
                except Exception, e:
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
            else:
                # Legacy code using HBase
                caipirinha_config = current_app.config['CAIPIRINHA_CONFIG']
                limonero_config = caipirinha_config['services']['limonero']
                storage = limonero_service.get_storage_info(
                    limonero_config['url'],
                    str(limonero_config['auth_token']),
                    caipirinha_config['storage_id'])

                # Get HBase hostname and port
                parsed_url = urlparse.urlparse(storage['url'])
                host = parsed_url.hostname
                port = parsed_url.port

                # Create HBase connection
                connection = happybase.Connection(host=host, port=port)
                vis_table = connection.table('visualization')

                # Get visualization data and prepare a decoded response
                # NOTE: Column names in HBase are formatted as
                # 'col_family:column_name' and
                # this is the reason for the following key transformation

                row = vis_table.row(
                    b'{job_id}-{task_id}'.format(job_id=job_id,
                                                 task_id=task_id))
                # Close HBase connection
                connection.close()
                if row:
                    data = json.loads(row.get('cf:data'))
                    labels = [l.strip() for l in
                              row.get('cf:column_names', '').split(',')]
                    schema = row.get('cf:schema')
                    if schema != '':
                        attributes = json.loads(schema)['fields']
                    else:
                        attributes = []
                else:
                    data = []
                    labels = []
                    attributes = []

            result = dict(
                job_id=job_id, task_id=task_id,
                # suggested_width=visualization.suggested_width,
                type=dict(id=visualization.type_id,
                          icon=visualization.type.icon,
                          name=visualization.type.name),
                title=visualization.title,
                # labels=labels,
                # attributes=attributes,
                data=data.get('data', data),
                legend=data.get('legend'),
                tooltip=data.get('tooltip'),
                x=data.get('x'),
                y=data.get('y'),
            )
        # In case of no visualization found
        else:
            result = dict(status="ERROR", message="Not Found"), 404
        return result
