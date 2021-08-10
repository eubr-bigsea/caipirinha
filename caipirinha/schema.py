# -*- coding: utf-8 -*-
import datetime
import json
from copy import deepcopy
from marshmallow import Schema, fields, post_load, post_dump, EXCLUDE, INCLUDE
from marshmallow.validate import OneOf
from flask_babel import gettext
from caipirinha.models import *


def partial_schema_factory(schema_cls):
    schema = schema_cls(partial=True)
    for field_name, field in list(schema.fields.items()):
        if isinstance(field, fields.Nested):
            new_field = deepcopy(field)
            new_field.schema.partial = True
            schema.fields[field_name] = new_field
    return schema


def translate_validation(validation_errors):
    for field, errors in list(validation_errors.items()):
        if isinstance(errors, dict):
            validation_errors[field] = translate_validation(errors)
        else:
            validation_errors[field] = [gettext(error) for error in errors]
        return validation_errors


def load_json(str_value):
    try:
        return json.loads(str_value)
    except BaseException:
        return None


# region Protected
class UserCreateRequestSchema(Schema):
    id = fields.Integer(required=True)
    login = fields.String(required=True)
    name = fields.String(required=True)

# endregion


class BaseSchema(Schema):
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None  # Empty lists must be kept!
        }


class DashboardListResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    created = fields.DateTime(
        required=False,
        allow_none=True,
        missing=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow)
    updated = fields.DateTime(
        required=False,
        allow_none=True,
        missing=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow)
    version = fields.Integer(required=True)
    task_id = fields.String(required=True)
    job_id = fields.Integer(required=True)
    configuration = fields.Function(lambda x: load_json(x.configuration))
    is_public = fields.Boolean(
        required=False,
        allow_none=True,
        missing=False,
        default=False)
    hash = fields.String(required=False, allow_none=True)
    user = fields.Function(
        lambda x: {
            "id": x.user_id,
            "name": x.user_name,
            "login": x.user_login})
    workflow = fields.Function(
        lambda x: {
            "id": x.workflow_id,
            "name": x.workflow_name})

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Dashboard"""
        return Dashboard(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class DashboardCreateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    title = fields.String(required=True)
    user_id = fields.Integer(required=True)
    user_login = fields.String(required=True)
    user_name = fields.String(required=True)
    workflow_id = fields.Integer(required=True)
    workflow_name = fields.String(required=False, allow_none=True)
    task_id = fields.String(required=True)
    job_id = fields.Integer(required=True)
    configuration = fields.String(required=False, allow_none=True)
    is_public = fields.Boolean(
        required=False,
        allow_none=True,
        missing=False,
        default=False)
    hash = fields.String(required=False, allow_none=True)
    visualizations = fields.Nested(
        'caipirinha.schema.VisualizationCreateRequestSchema',
        allow_none=True,
        many=True)
    user = fields.Nested(
        'caipirinha.schema.UserCreateRequestSchema',
        allow_none=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Dashboard"""
        return Dashboard(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class DashboardItemResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    title = fields.String(required=True)
    created = fields.DateTime(
        required=False,
        allow_none=True,
        missing=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow)
    updated = fields.DateTime(
        required=False,
        allow_none=True,
        missing=datetime.datetime.utcnow,
        default=datetime.datetime.utcnow)
    version = fields.Integer(required=True)
    task_id = fields.String(required=True)
    job_id = fields.Integer(required=True)
    configuration = fields.Function(lambda x: load_json(x.configuration))
    is_public = fields.Boolean(
        required=False,
        allow_none=True,
        missing=False,
        default=False)
    hash = fields.String(required=False, allow_none=True)
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

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Dashboard"""
        return Dashboard(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class VisualizationCreateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    task_id = fields.String(required=True)
    title = fields.String(required=True)
    workflow_id = fields.Integer(required=False, allow_none=True)
    job_id = fields.Integer(required=False, allow_none=True)
    suggested_width = fields.Integer(
        required=False,
        allow_none=True,
        missing=12,
        default=12)
    data = fields.String(required=False, allow_none=True)
    type = fields.Nested(
        'caipirinha.schema.VisualizationTypeCreateRequestSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Visualization"""
        return Visualization(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class VisualizationListResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    task_id = fields.String(required=True)
    title = fields.String(required=True)
    workflow_id = fields.Integer(required=False, allow_none=True)
    job_id = fields.Integer(required=False, allow_none=True)
    suggested_width = fields.Integer(
        required=False,
        allow_none=True,
        missing=12,
        default=12)
    data = fields.String(required=False, allow_none=True)
    type = fields.Nested(
        'caipirinha.schema.VisualizationTypeListResponseSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Visualization"""
        return Visualization(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class VisualizationItemResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    task_id = fields.String(required=True)
    title = fields.String(required=True)
    workflow_id = fields.Integer(required=False, allow_none=True)
    job_id = fields.Integer(required=False, allow_none=True)
    suggested_width = fields.Integer(
        required=False,
        allow_none=True,
        missing=12,
        default=12)
    data = fields.String(required=False, allow_none=True)
    type = fields.Nested(
        'caipirinha.schema.VisualizationTypeItemResponseSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of Visualization"""
        return Visualization(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class VisualizationTypeCreateRequestSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    icon = fields.String(required=False, allow_none=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of VisualizationType"""
        return VisualizationType(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class VisualizationTypeItemResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    help = fields.String(required=True)
    icon = fields.String(required=False, allow_none=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of VisualizationType"""
        return VisualizationType(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE


class VisualizationTypeListResponseSchema(BaseSchema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    help = fields.String(required=True)
    icon = fields.String(required=False, allow_none=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data, **kwargs):
        """ Deserialize data into an instance of VisualizationType"""
        return VisualizationType(**data)

    class Meta:
        ordered = True
        unknown = EXCLUDE

