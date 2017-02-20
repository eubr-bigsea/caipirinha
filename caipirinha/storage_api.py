# -*- coding: utf-8 -*-}
from app_auth import requires_auth
from flask import request, current_app
from flask_restful import Resource
from schema import *


class StorageListApi(Resource):
    """ REST API for listing class Storage """

    @staticmethod
    @requires_auth
    def get():
        only = ('id', 'name') \
            if request.args.get('simple', 'false') == 'true' else None
        storages = Storage.query.all()

        return StorageListResponseSchema(
            many=True, only=only).dump(storages).data


class StorageDetailApi(Resource):
    """ REST API for a single instance of class Storage """

    @staticmethod
    @requires_auth
    def get(storage_id):
        storage = Storage.query.get(storage_id)
        if storage is not None:
            return StorageItemResponseSchema().dump(storage).data
        else:
            return dict(status="ERROR", message="Not found"), 404
