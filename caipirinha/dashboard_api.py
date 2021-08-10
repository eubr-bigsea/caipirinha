# -*- coding: utf-8 -*-}
import logging
import math
import uuid

from sqlalchemy import or_
from caipirinha.app_auth import requires_auth
from caipirinha.schema import *
from flask import request, current_app
from flask_restful import Resource
from marshmallow.exceptions import ValidationError
from gettext import gettext

log = logging.getLogger(__name__)


def _get_dashboards(dashboards):
    # return dashboards.filter(Dashboard.user_id == g.user.id)
    return dashboards


class DashboardListApi(Resource):
    """ REST API for listing class Dashboard """

    @staticmethod
    @requires_auth
    def get():
        only = None if request.args.get('simple') != 'true' else ('id',)
        if request.args.get('fields'):
            only = tuple(
                [x.strip() for x in request.args.get('fields').split(',')])

        dashboards = _get_dashboards(Dashboard.query)

        sort = request.args.get('sort', 'title')
        if sort not in ['title']:
            sort = 'id'
        sort_option = getattr(Dashboard, sort)
        if request.args.get('asc', 'true') == 'false':
            sort_option = sort_option.desc()

        dashboards = dashboards.order_by(sort_option)
        q_filter = request.args.get('q')
        if q_filter:
            find_pattern = f'%%{q_filter.replace(" ", "%")}%%'
            dashboards = dashboards.filter(or_(
                Dashboard.title.like(find_pattern),
                Dashboard.user_name.like(find_pattern)))

        page = request.args.get('page') or '1'

        if page is not None and page.isdigit():
            page_size = int(request.args.get('size', 20))
            page = int(page)
            pagination = dashboards.paginate(page, page_size, True)
            result = {
                'data': DashboardListResponseSchema(many=True, only=only).dump(
                    pagination.items),
                'pagination': {
                    'page': page, 'size': page_size,
                    'total': pagination.total,
                    'pages': int(math.ceil(1.0 * pagination.total / page_size))}
            }
        else:
            result = {
                'data': DashboardListResponseSchema(many=True, only=only).dump(
                    dashboards)}

        return result

    @staticmethod
    @requires_auth
    def post():
        result, result_code = dict(
            status="ERROR", message="Missing json in the request body"), 400
        if request.data is not None:
            data = json.loads(request.data)
            request_schema = DashboardCreateRequestSchema()
            response_schema = DashboardItemResponseSchema()

            params = {}
            params.update(data)

            if 'user' in params:
                user = params.pop('user')
                params['user_id'] = user['id']
                params['user_login'] = user['login']
                params['user_name'] = user['name']

            params['workflow_id'] = params.get('workflow', {}).get(
                'id') or params.get('workflow_id')
            params['workflow_name'] = params.get('workflow', {}).get(
                'name') or params.get('workflow_name')

            try:
                dashboard = request_schema.load(params)
                # fix foreign keys
                for visualization in dashboard.visualizations:
                    visualization.type = VisualizationType.query.get(
                        visualization.type.id)

                # pdb.set_trace()
                db.session.add(dashboard)
                db.session.commit()
                result, result_code = response_schema.dump(
                    dashboard), 200
            except ValidationError as e:
                result= {
                   'status': 'ERROR', 
                   'message': gettext('Validation error'),
                   'errors': e.messages
                }
            except Exception as e:
                log.exception('Error in POST')
                result, result_code = dict(status="ERROR",
                                           message="Internal error"), 500
                if current_app.debug:
                    result['debug_detail'] = str(e)
                db.session.rollback()

        return result, result_code

def get_dashboard(dashboard_id):
    if dashboard_id is not None:
        result = DashboardItemResponseSchema().dump(dashboard_id)
        if result.get('configuration') is not None:
            try:
                result['configuration'] = json.loads(result['configuration'])
            except:
                ...
        for visualization in result.get('visualizations', []):
            if 'data' in visualization:
                del visualization['data']
        return result
    else:
        return dict(status="ERROR", message="Not found"), 404


class PublicDashboardApi(Resource):
    @staticmethod
    def get(h):
        return get_dashboard(Dashboard.query.filter(
            Dashboard.hash==h).first())


class DashboardDetailApi(Resource):
    """ REST API for a single instance of class Dashboard """

    @staticmethod
    @requires_auth
    def get(dashboard_id):
        return get_dashboard(Dashboard.query.get(dashboard_id))

    @staticmethod
    @requires_auth
    def delete(dashboard_id):
        result, result_code = dict(status="ERROR", message="Not found"), 404

        dashboard = Dashboard.query.get(dashboard_id)
        if dashboard is not None:
            try:
                db.session.delete(dashboard)
                db.session.commit()
                result, result_code = dict(status="OK", message="Deleted"), 201
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
    def patch(dashboard_id):
        result = dict(status="ERROR", message="Insufficient data")
        result_code = 400

        if request.json:
            data = request.json
            if 'configuration' in data:
                data['configuration'] = json.dumps(data['configuration'])
            # Cannot be changed
            if 'user' in data:
                del data['user']
            if 'visualizations' in data:
                del data['visualizations']
            request_schema = partial_schema_factory(
                DashboardCreateRequestSchema)
            response_schema = DashboardItemResponseSchema()
            try:
            # Ignore missing fields to allow partial updates
                dashboard = request_schema.load(data, partial=True)
                dashboard.id = dashboard_id
                if dashboard.is_public and dashboard.hash is None:
                    dashboard.hash = uuid.uuid4().hex
                dashboard = db.session.merge(dashboard)
                db.session.commit()

                if dashboard is not None:
                    result, result_code = dict(
                        status="OK", message="Updated",
                        data=response_schema.dump(dashboard)), 200
                else:
                    result = dict(status="ERROR", message="Not found")
            except ValidationError as e:
                result= {
                   'status': 'ERROR', 
                   'message': gettext('Validation error'),
                   'errors': e.messages
                }
            except Exception as e:
                log.exception('Error in PATCH')
                result, result_code = dict(status="ERROR",
                                           message="Internal error"), 500
                if current_app.debug:
                    result['debug_detail'] = str(e)
                db.session.rollback()
        return result, result_code
