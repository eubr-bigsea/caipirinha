# -*- coding: utf-8 -*-
import json
import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, \
    Enum, DateTime, Numeric, Text, Unicode, UnicodeText
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy_i18n import make_translatable, translation_base, Translatable

make_translatable(options={'locales': ['pt', 'en', 'es'],
                           'auto_create_locales': True,
                           'fallback_locale': 'en'})

db = SQLAlchemy()


class Dashboard(db.Model):
    """ A dashboard containing visualizations created by Lemonade """
    __tablename__ = 'dashboard'

    # Fields
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    created = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)
    updated = Column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)
    version = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    user_login = Column(String(50), nullable=False)
    user_name = Column(String(200), nullable=False)
    workflow_id = Column(Integer, nullable=False)
    workflow_name = Column(String(200))

    def __unicode__(self):
        return self.title

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)


class Visualization(db.Model):
    """ A visualization created by Lemonade """
    __tablename__ = 'visualization'

    # Fields
    id = Column(String(250), primary_key=True,
                autoincrement=False)
    suggested_width = Column(Integer, nullable=False, default=12)

    # Associations
    dashboard_id = Column(Integer,
                          ForeignKey("dashboard.id"), nullable=False)
    dashboard = relationship("Dashboard", foreign_keys=[dashboard_id],
                             backref=backref(
                                 "visualizations",
                                 cascade="all, delete-orphan"))
    type_id = Column(Integer,
                     ForeignKey("visualization_type.id"), nullable=False)
    type = relationship("VisualizationType", foreign_keys=[type_id])

    def __unicode__(self):
        return self.suggested_width

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)


class VisualizationType(db.Model):
    """ Type of visualization """
    __tablename__ = 'visualization_type'

    # Fields
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    help = Column(String(500), nullable=False)
    icon = Column(String(200))

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)

