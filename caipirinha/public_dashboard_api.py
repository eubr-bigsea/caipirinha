# -*- coding: utf-8 -*-}

from caipirinha.app_auth import requires_auth
from caipirinha.schema import *
from flask.views import MethodView
from .dashboard_api import get_dashboard


class PublicDashboardApi(MethodView):
    @staticmethod
    def get(h):
        return get_dashboard(Dashboard.query.filter(
            Dashboard.hash == h).first())
