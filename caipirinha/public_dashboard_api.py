# -*- coding: utf-8 -*-}

from caipirinha.app_auth import requires_auth
from caipirinha.schema import *
from flask_restful import Resource
from .dashboard_api import get_dashboard


class PublicDashboardApi(Resource):
    @staticmethod
    def get(h):
        return get_dashboard(Dashboard.query.filter(
            Dashboard.hash == h).first())
