import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, \
    Enum, DateTime, Numeric, Text, Unicode, UnicodeText
from sqlalchemy import event
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy_i18n import make_translatable, translation_base, Translatable

make_translatable(options={'locales': ['pt', 'en'],
                           'auto_create_locales': True,
                           'fallback_locale': 'en'})

db = SQLAlchemy()

# Association tables definition


class Dashboard(db.Model):
    """ A dashboard containing visualizations created by Lemonade """
    __tablename__ = 'dashboard'

    # Fields
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    created = Column(DateTime,
                     default=datetime.datetime.utcnow, nullable=False,
                     onupdate=datetime.datetime.utcnow)
    updated = Column(DateTime,
                     default=datetime.datetime.utcnow, nullable=False,
                     onupdate=datetime.datetime.utcnow)
    version = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    user_login = Column(String(50), nullable=False)
    user_name = Column(String(200), nullable=False)
    workflow_id = Column(Integer, nullable=False)
    workflow_name = Column(String(200))
    task_id = Column(String(200), nullable=False)
    job_id = Column(Integer, nullable=False)
    configuration = Column(LONGTEXT)
    is_public = Column(Boolean,
                       default=False, nullable=False)
    hash = Column(String(200))
    __mapper_args__ = {
        'version_id_col': version,
    }

    # Associations
    visualizations = relationship("Visualization", back_populates="dashboard",
                                  cascade="all, delete-orphan")

    def __str__(self):
        return self.title

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)


class Visualization(db.Model):
    """ A visualization created by Lemonade """
    __tablename__ = 'visualization'

    # Fields
    id = Column(Integer, primary_key=True)
    task_id = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    workflow_id = Column(Integer)
    job_id = Column(Integer)
    suggested_width = Column(Integer,
                             default=12)
    data = Column(LONGTEXT)

    # Associations
    dashboard_id = Column(Integer,
                          ForeignKey("dashboard.id",
                                     name="fk_dashboard_id"))
    dashboard = relationship(
        "Dashboard",
        foreign_keys=[dashboard_id],
        # No cascade!!!
        back_populates="visualizations"
    )
    type_id = Column(Integer,
                     ForeignKey("visualization_type.id",
                                name="fk_visualization_type_id"), nullable=False)
    type = relationship(
        "VisualizationType",
        foreign_keys=[type_id])

    def __str__(self):
        return self.task_id

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

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)

