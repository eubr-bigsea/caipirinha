# -*- coding: utf-8 -*-
import datetime
import json
from copy import deepcopy
from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf
from models import *


def partial_schema_factory(schema_cls):
    schema = schema_cls(partial=True)
    for field_name, field in schema.fields.items():
        if isinstance(field, fields.Nested):
            new_field = deepcopy(field)
            new_field.schema.partial = True
            schema.fields[field_name] = new_field
    return schema


def load_json(str_value):
    try:
        return json.loads(str_value)
    except:
        return "Error loading JSON"


# region Protected\s*
# endregion


class DashboardListResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    created = fields.DateTime(required=True, missing=datetime.datetime.utcnow,
                              default=datetime.datetime.utcnow)
    updated = fields.DateTime(required=True, missing=datetime.datetime.utcnow,
                              default=datetime.datetime.utcnow)
    version = fields.Integer(required=True)
    workflow_id = fields.Integer(required=True)
    workflow_name = fields.String(required=False, allow_none=True)
    user = fields.Function(
        lambda x: {
            "id": x.user_id,
            "name": x.user_name,
            "login": x.user_login})

    class Meta:
        ordered = True


class DashboardCreateRequestSchema(Schema):
    """ JSON serialization schema """
    title = fields.String(required=True)
    user_id = fields.Integer(required=True)
    user_login = fields.String(required=True)
    user_name = fields.String(required=True)
    workflow_id = fields.Integer(required=True)
    workflow_name = fields.String(required=False, allow_none=True)
    user = fields.Nested(
        'caipirinha.schema.UserCreateRequestSchema',
        allow_none=True)

    class Meta:
        ordered = True


class DashboardItemResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    created = fields.DateTime(required=True, missing=datetime.datetime.utcnow,
                              default=datetime.datetime.utcnow)
    updated = fields.DateTime(required=True, missing=datetime.datetime.utcnow,
                              default=datetime.datetime.utcnow)
    version = fields.Integer(required=True)
    workflow_id = fields.Integer(required=True)
    workflow_name = fields.String(required=False, allow_none=True)
    user = fields.Function(
        lambda x: {
            "id": x.user_id,
            "name": x.user_name,
            "login": x.user_login})

    class Meta:
        ordered = True

