# -*- coding: utf-8 -*-}
import logging
import math
import uuid

from sqlalchemy import or_
from caipirinha.app_auth import requires_auth
from caipirinha.schema import *
from flask import request, current_app
from flask_restful import Resource

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
            find_pattern = '%%{}%%'.format(q_filter.replace(" ", "%"))
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
                    pagination.items).data,
                'pagination': {
                    'page': page, 'size': page_size,
                    'total': pagination.total,
                    'pages': int(math.ceil(1.0 * pagination.total / page_size))}
            }
        else:
            result = {
                'data': DashboardListResponseSchema(many=True, only=only).dump(
                    dashboards).data}

        return result

    @staticmethod
    @requires_auth
    def post():
        result, result_code = dict(
            status="ERROR", message="Missing json in the request body"), 401
        if request.data is not None:
            data = json.loads(request.data)
            request_schema = DashboardCreateRequestSchema()
            response_schema = DashboardItemResponseSchema()

            params = {}
            params.update(data)

            user = params.pop('user')
            params['user_id'] = user['id']
            params['user_login'] = user['login']
            params['user_name'] = user['name']
            params['workflow_id'] = params.get('workflow', {}).get(
                'id') or params.get('workflow_id')
            params['workflow_name'] = params.get('workflow', {}).get(
                'name') or params.get('workflow_name')

            form = request_schema.load(params)
            if form.errors:
                result, result_code = dict(
                    status="ERROR", message="Validation error",
                    errors=form.errors), 401
            else:
                try:
                    dashboard = form.data
                    # fix foreign keys
                    for i in range(len(dashboard.visualizations)):
                        dashboard.visualizations[i].type = \
                            VisualizationType.query.get(
                                dashboard.visualizations[i].type.id)
                        # dashboard.visualizations[i].type = None

                    # pdb.set_trace()
                    db.session.add(dashboard)
                    db.session.commit()
                    result, result_code = response_schema.dump(
                        dashboard).data, 200
                except Exception as e:
                    log.exception('Error in POST')
                    result, result_code = dict(status="ERROR",
                                               message="Internal error"), 500
                    if current_app.debug:
                        result['debug_detail'] = str(e)
                    db.session.rollback()

        return result, result_code

def _get_dashboard(dashboard):
    if dashboard is not None:
        result = DashboardItemResponseSchema().dump(dashboard).data
        if result.get('configuration') is not None:
            result['configuration'] = json.loads(result['configuration'])
        for visualization in result.get('visualizations', []):
            del visualization['data']
        return result
    else:
        return dict(status="ERROR", message="Not found"), 404


class PublicDashboardApi(Resource):
    @staticmethod
    def get(h):
        return _get_dashboard(Dashboard.query.filter(
            Dashboard.hash==h).first())


class DashboardDetailApi(Resource):
    """ REST API for a single instance of class Dashboard """

    @staticmethod
    @requires_auth
    def get(dashboard_id):
        return _get_dashboard(Dashboard.query.get(dashboard_id))

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
        result_code = 404

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
            # Ignore missing fields to allow partial updates
            form = request_schema.load(data, partial=True)
            response_schema = DashboardItemResponseSchema()
            if not form.errors:
                try:
                    form.data.id = dashboard_id
                    if form.data.is_public and form.data.hash is None:
                        form.data.hash = uuid.uuid4().hex
                    dashboard = db.session.merge(form.data)
                    db.session.commit()

                    if dashboard is not None:
                        result, result_code = dict(
                            status="OK", message="Updated",
                            data=response_schema.dump(dashboard).data), 200
                    else:
                        result = dict(status="ERROR", message="Not found")
                except Exception as e:
                    log.exception('Error in PATCH')
                    result, result_code = dict(status="ERROR",
                                               message="Internal error"), 500
                    if current_app.debug:
                        result['debug_detail'] = str(e)
                    db.session.rollback()
            else:
                result = dict(status="ERROR", message="Invalid data",
                              errors=form.errors)
        return result, result_code
