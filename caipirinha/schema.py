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

class UserCreateRequestSchema(Schema):
    id = fields.Integer(required=True)
    login = fields.String(required=True)
    name = fields.String(required=True)

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
    task_id = fields.String(required=True)
    job_id = fields.Integer(required=True)
    visualizations = fields.Nested(
        'caipirinha.schema.VisualizationListResponseSchema',
        allow_none=True,
        many=True)
    user = fields.Function(
        lambda x: {
            "id": x.user_id,
            "name": x.user_name,
            "login": x.user_login})
    workflow = fields.Function(
        lambda x: {
            "id": x.workflow_id,
            "name": x.workflow_name})

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
    task_id = fields.String(required=True)
    job_id = fields.Integer(required=True)
    visualizations = fields.Nested(
        'caipirinha.schema.VisualizationCreateRequestSchema',
        allow_none=True,
        many=True)
    user = fields.Nested(
        'caipirinha.schema.UserCreateRequestSchema',
        allow_none=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Dashboard"""
        return Dashboard(**data)

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
    task_id = fields.String(required=True)
    job_id = fields.Integer(required=True)
    visualizations = fields.Nested(
        'caipirinha.schema.VisualizationItemResponseSchema',
        allow_none=True,
        many=True)
    user = fields.Function(
        lambda x: {
            "id": x.user_id,
            "name": x.user_name,
            "login": x.user_login})
    workflow = fields.Function(
        lambda x: {
            "id": x.workflow_id,
            "name": x.workflow_name})

    class Meta:
        ordered = True


class VisualizationCreateRequestSchema(Schema):
    """ JSON serialization schema """
    task_id = fields.String(required=True)
    title = fields.String(required=True)
    job_id = fields.Integer(required=True)
    suggested_width = fields.Integer(required=True, missing=12,
                                     default=12)
    type = fields.Nested(
        'caipirinha.schema.VisualizationTypeCreateRequestSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Visualization"""
        return Visualization(**data)

    class Meta:
        ordered = True


class VisualizationListResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    task_id = fields.String(required=True)
    title = fields.String(required=True)
    job_id = fields.Integer(required=True)
    suggested_width = fields.Integer(required=True, missing=12,
                                     default=12)
    type = fields.Nested(
        'caipirinha.schema.VisualizationTypeListResponseSchema',
        required=True)

    class Meta:
        ordered = True


class VisualizationItemResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    task_id = fields.String(required=True)
    title = fields.String(required=True)
    job_id = fields.Integer(required=True)
    suggested_width = fields.Integer(required=True, missing=12,
                                     default=12)
    type = fields.Nested(
        'caipirinha.schema.VisualizationTypeItemResponseSchema',
        required=True)

    class Meta:
        ordered = True


class VisualizationTypeCreateRequestSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    icon = fields.String(required=False, allow_none=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of VisualizationType"""
        return VisualizationType(**data)

    class Meta:
        ordered = True


class VisualizationTypeItemResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    help = fields.String(required=True)
    icon = fields.String(required=False, allow_none=True)

    class Meta:
        ordered = True


class VisualizationTypeListResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    help = fields.String(required=True)
    icon = fields.String(required=False, allow_none=True)

    class Meta:
        ordered = True

