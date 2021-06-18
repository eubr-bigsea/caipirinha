import os
import tempfile

import pytest

import flask_migrate
from caipirinha.app import create_app
from caipirinha.models import db

@pytest.fixture
def client():
    app = create_app()
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///tests/test.db'
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            flask_migrate.upgrade(revision='head')
        yield client

