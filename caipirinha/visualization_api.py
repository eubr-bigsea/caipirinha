# -*- coding: utf-8 -*-}

import json
import urlparse

import happybase
from app_auth import requires_auth
from caipirinha.service import limonero_service
from flask import current_app
from flask_restful import Resource
from schema import *


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
                b'{job_id}-{task_id}'.format(job_id=job_id, task_id=task_id))
            # Close HBase connection
            connection.close()
            if row:
                data = json.loads(row.get('cf:data'))
                labels = [l.strip() for l in
                          row.get('cf:column_names', '').split(',')]
                attributes = json.loads(row.get('cf:schema'))['fields']
            else:
                data = []
                labels = []
                attributes = []

            result = dict(
                job_id=job_id, task_id=task_id,
                suggested_width=visualization.suggested_width,
                type=dict(id=visualization.type_id,
                          icon=visualization.type.icon,
                          name=visualization.type.name),
                title=row.get('cf:title') if row else '',
                labels=labels,
                attributes=attributes,
                data=data)
        # In case of no visualization found
        else:
            result = dict(status="ERROR", message="Not Found"), 404
        return result
