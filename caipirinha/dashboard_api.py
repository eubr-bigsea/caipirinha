# -*- coding: utf-8 -*-}
from app_auth import requires_auth
from flask import request, current_app
from flask_restful import Resource
from schema import *


class DashboardListApi(Resource):
    """ REST API for listing class Dashboard """

    @staticmethod
    @requires_auth
    def get():
        if request.args.get('fields'):
            only = [f.strip() for f in
                    request.args.get('fields').split(',')]
        else:
            only = ('id', 'name') if request.args.get(
                'simple', 'false') == 'true' else None
        dashboards = Dashboard.query.all()

        return DashboardListResponseSchema(
            many=True, only=only).dump(dashboards).data

    @staticmethod
    @requires_auth
    def post():
        result, result_code = dict(
            status="ERROR", message="Missing json in the request body"), 401
        if request.json is not None:
            request_schema = DashboardCreateRequestSchema()
            response_schema = DashboardItemResponseSchema()
            form = request_schema.load(request.json)
            if form.errors:
                result, result_code = dict(
                    status="ERROR", message="Validation error",
                    errors=form.errors), 401
            else:
                try:
                    dashboard = form.data
                    db.session.add(dashboard)
                    db.session.commit()
                    result, result_code = response_schema.dump(
                        dashboard).data, 200
                except Exception, e:
                    result, result_code = dict(status="ERROR",
                                               message="Internal error"), 500
                    if current_app.debug:
                        result['debug_detail'] = e.message
                    db.session.rollback()

        return result, result_code


class DashboardDetailApi(Resource):
    """ REST API for a single instance of class Dashboard """

    @staticmethod
    @requires_auth
    def get(dashboard_id):
        dashboard = Dashboard.query.get(dashboard_id)
        if dashboard is not None:
            return DashboardItemResponseSchema().dump(dashboard).data
        else:
            return dict(status="ERROR", message="Not found"), 404

    @staticmethod
    @requires_auth
    def delete(dashboard_id):
        result, result_code = dict(status="ERROR", message="Not found"), 404

        dashboard = Dashboard.query.get(dashboard_id)
        if dashboard is not None:
            try:
                db.session.delete(dashboard)
                db.session.commit()
                result, result_code = dict(status="OK", message="Deleted"), 200
            except Exception, e:
                result, result_code = dict(status="ERROR",
                                           message="Internal error"), 500
                if current_app.debug:
                    result['debug_detail'] = e.message
                db.session.rollback()
        return result, result_code

    @staticmethod
    @requires_auth
    def patch(dashboard_id):
        result = dict(status="ERROR", message="Insufficient data")
        result_code = 404

        if request.json:
            request_schema = partial_schema_factory(DashboardCreateRequestSchema)
            # Ignore missing fields to allow partial updates
            form = request_schema.load(request.json, partial=True)
            response_schema = DashboardItemResponseSchema()
            if not form.errors:
                try:
                    form.data.id = dashboard_id
                    dashboard = db.session.merge(form.data)
                    db.session.commit()

                    if dashboard is not None:
                        result, result_code = dict(
                            status="OK", message="Updated",
                            data=response_schema.dump(dashboard).data), 200
                    else:
                        result = dict(status="ERROR", message="Not found")
                except Exception, e:
                    result, result_code = dict(status="ERROR",
                                               message="Internal error"), 500
                    if current_app.debug:
                        result['debug_detail'] = e.message
                    db.session.rollback()
            else:
                result = dict(status="ERROR", message="Invalid data",
                            errors=form.errors)
        return result, result_code

