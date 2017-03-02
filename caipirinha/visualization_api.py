# -*- coding: utf-8 -*-}
from app_auth import requires_auth
from flask import request, current_app
from flask_restful import Resource
from schema import *
from caipirinha.runner import configuration
from caipirinha.service import limonero_service
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
import json
import happybase
import urlparse

class VisualizationDetailApi(Resource):
    """ REST API for a single instance of class Visualization """

    @staticmethod
    @requires_auth
    def get(job_id, task_id):

        # Check the existence of such visualization
        vis_query = Visualization.query.filter(
                Visualization.job_id == int(job_id),
                Visualization.task_id == str(task_id))

        # Try to get one single value (this is the expected)
        try:
            # NOTE: For now we do not use this information to generate the
            # visualization. We just want to check its availability in the
            # relational database
            visualization = vis_query.one()
            vis_metadata = VisualizationItemResponseSchema().dump(visualization).data

        # In case of database inconsistency: multiple visualizations with the
        # same 'job_id' and 'task_id'
        except MultipleResultsFound as me:
            return dict(status="ERROR",
            message="Ambiguous visualization (multiple results)"), 404

        # In case of no visualization found
        except NoResultFound as ne:
            return dict(status="ERROR", message="Not Found"), 404

        # Retrieve visualization user data from Caipirinha storage
        caipirinha_config = configuration.get_config()['caipirinha']
        limonero_config = caipirinha_config['services']['limonero']
        storage = limonero_service.get_storage_info(
                limonero_config['url'],
                str(limonero_config['auth_token']), caipirinha_config['storage_id'])

        # Get hbase hostname and port
        parsed_url = urlparse.urlparse(storage['url'])
        host = parsed_url.hostname
        port = parsed_url.port

        # Create HBase connection
	connection = happybase.Connection(host=host, port=port)
	vis_table = connection.table('visualization')

        # Get visualization data and prepare a decoded response
        # NOTE: Column names in HBase are formated as 'col_family:column_name' and
        # this is the reason for the following key transformation
        vis_row = vis_table.row(
                b'{job_id}-{task_id}'.format(job_id=job_id,task_id=task_id))
        result = {col.split(':')[1]: json.loads(value) \
                for col,value in vis_row.items()}
        result['job_id'] = job_id
        result['task_id'] = task_id

        # Close HBase connection
        connection.close()

        return result
