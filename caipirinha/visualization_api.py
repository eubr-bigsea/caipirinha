# -*- coding: utf-8 -*-}
import urlparse

import happybase
from app_auth import requires_auth
from flask import request, current_app
from flask_restful import Resource
from schema import *


class VisualizationDetailApi(Resource):
    """ REST API for a single instance of class Visualization """

    @staticmethod
    @requires_auth
    def get(job_id, task_id):
        config = current_app.config['CAIPIRINHA_CONFIG']
        hbase_url = config.get('servers', {}).get('hbase_url')

        if hbase_url is not None:
            parsed_url = urlparse.urlparse(hbase_url)
            visualization = Visualization.query.filter(
                Visualization.job_id == job_id,
                Visualization.task_id == task_id).first()

            if visualization is not None:
                hbase_conn = happybase.Connection(
                    host=parsed_url.hostname,
                    port=parsed_url.port or 9090)
                vis_table = hbase_conn.table('visualization')
                row = vis_table.row(b'{job_id}-{task_id}'.format(
                    job_id=job_id, task_id=task_id))

                data = json.loads(row.get('cf:data'))
                result = dict(
                    job_id=job_id, task_id=task_id,
                    suggested_width=visualization.suggested_width,
                    type=dict(id=visualization.type_id,
                              icon=visualization.type.icon,
                              name=visualization.type.name),
                    title=row.get('cf:title'),
                    labels=[l.strip() for l in
                            row.get('cf:column_names', '').split(',')],
                    attributes=json.loads(row.get('cf:schema'))['fields'],
                    data=data)
                hbase_conn.close()
                return result
            else:
                return dict(status="ERROR", message="Not found"), 404
        else:
            return dict(status="ERROR",
                        message="Missing hbase configuration"), 500
