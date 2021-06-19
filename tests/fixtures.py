import json
import os
import pytest

import flask_migrate
from caipirinha.app import create_app
from caipirinha.models import (Dashboard, Visualization, db)


def get_visualizations():
    v1 = Visualization(
        id=1, title='First visualization', task_id=1,
        workflow_id=1, job_id=1, data='{}', dashboard_id=2000, type_id=19)

    v2 = Visualization(
        id=2, title='Second visualization', task_id=2,
        workflow_id=2, job_id=2, data='{}', dashboard_id=2000, type_id=89)

    data3 = {
        'type': 'barchart',
        'data': [[2, 3], [4, 4]]
    }
    v2 = Visualization(
        id=3, title='Third visualization', task_id=3,
        workflow_id=3, job_id=3, data=json.dumps(data3), dashboard_id=2000, type_id=123)
    return [v1, v2]


def get_dashboards():
    v1 = Visualization(
        id=0, title='First visualization', task_id=1,
        workflow_id=1, job_id=1, data='{}', dashboard_id=1, type_id=70)
    return [
        Dashboard(id=1000, title='Example', hash='343',
                  user_id=1, user_name='admin', user_login='admin',
                  workflow_id=1, workflow_name='First workflow',
                  task_id=1, job_id=1,
                  visualizations=[
                      v1
                  ]),
        Dashboard(id=2000, title='With visualizations', hash='1343',
                  user_id=1, user_name='admin', user_login='admin',
                  workflow_id=11, workflow_name='Second workflow',
                  task_id=11, job_id=2),

        Dashboard(id=3000, title='Public dashboard', hash='007',
                  user_id=1, user_name='admin', user_login='admin',
                  workflow_id=11, workflow_name='Scond workflow',
                  task_id=11, job_id=2, is_public=True),

        Dashboard(id=4000, title='No visualization', hash='1343',
                  user_id=1, user_name='admin', user_login='admin',
                  workflow_id=11, workflow_name='Fourth workflow',
                  task_id=11, job_id=2,
                  configuration='{}'),
    ]


@pytest.fixture(scope='session')
def client():
    app = create_app()
    path = os.path.dirname(os.path.abspath(__name__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{path}/test.db'
    app.config['TESTING'] = True
    # import pdb; pdb.set_trace()
    with app.test_client() as client:
        with app.app_context():
            flask_migrate.downgrade(revision="base")
            flask_migrate.upgrade(revision='head')
            for dashboard in get_dashboards():
                db.session.add(dashboard)
            for visualization in get_visualizations():
                db.session.add(visualization)
            client.secret = app.config['CAIPIRINHA_CONFIG']['secret']
            db.session.commit()
        yield client
