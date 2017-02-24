# -*- coding: utf-8 -*-}
from app_auth import requires_auth
from flask import request, current_app
from flask_restful import Resource
from schema import *


class VisualizationDetailApi(Resource):
    """ REST API for a single instance of class Visualization """

    @staticmethod
    @requires_auth
    def get(visualization_id):
        visualization = Visualization.query.get(visualization_id)
        if visualization is not None:
            return VisualizationItemResponseSchema().dump(visualization).data
        else:
            return dict(status="ERROR", message="Not found"), 404

