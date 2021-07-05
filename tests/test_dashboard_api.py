from .conftest import *
from flask import current_app


def test_get_dashboards_unauthorized(client):
    rv = client.get('/dashboards', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401

    rv = client.get('/dashboards/1', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401

    rv = client.post('/dashboards', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401

    rv = client.patch('/dashboards/1', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401

    rv = client.delete('/dashboards/1', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401


def test_get_dashboards(client):
    """Retrieve a list of dashboards."""

    headers = {'X-Auth-Token': str(client.secret)}
    rv = client.get('/dashboards', headers=headers)
    assert rv.json['pagination']['total'] == 4
    d1 = rv.json['data'][0]
    assert set(d1.keys()) == {'id', 'title', 'created', 'updated', 'version',
                              'task_id', 'job_id', 'is_public', 'hash', 'user',
                              'workflow'}
    assert rv.status_code == 200


def test_get_dashboards_filter(client):
    """Retrieve a list of dashboards."""

    headers = {'X-Auth-Token': str(client.secret)}
    rv = client.get('/dashboards?q=visualization', headers=headers)
    assert rv.json['pagination']['total'] == 2
    assert rv.status_code == 200

def test_get_dashboard(client):
    headers = {'X-Auth-Token': str(client.secret)}
    dashboard_id = 4000
    rv = client.get(f'/dashboards/{dashboard_id}', headers=headers)
    # Old style API. Change it in future
    d1 = rv.json
    
    assert rv.status_code == 200
    assert d1['title'] == 'No visualization'
    assert d1['hash'] == '1343'
    assert 'visualizations' not in d1
    assert set(d1.keys()) == {'id', 'title', 'created', 'updated', 'version',
                              'task_id', 'job_id', 'is_public', 'hash', 'user',
                              'workflow', 'configuration'}


def test_get_public_dashboard(client):
    """ Public dashboard can be accessed without a secret token"""
    headers = {}
    # Notice that here it is used the hash instead of id
    rv = client.get('/public/dashboard/007', headers=headers)
    assert rv.status_code == 200

    d1 = rv.json
    assert d1['title'] == 'Public dashboard'
    assert d1['is_public'] == True
    assert d1['hash'] == '007'
    assert set(d1.keys()) == {'id', 'title', 'created', 'updated', 'version',
                              'task_id', 'job_id', 'is_public', 'hash', 'user',
                              'workflow'}


def test_delete_dashboard(client):
    headers = {'X-Auth-Token': str(client.secret)}
    dashboard_id = 1000
    rv = client.delete(f'/dashboards/{dashboard_id}', headers=headers)
    assert rv.status_code == 201
    assert rv.json['status'] == 'OK'
    assert rv.json['message'] == 'Deleted'

    with current_app.app_context():
        assert Dashboard.query.get(1) is None
        assert Visualization.query.get(0) is None


def test_update_dashboard(client):
    headers = {'X-Auth-Token': str(client.secret)}

    # Missing data
    dashboard_id = 2000
    rv = client.patch(f'/dashboards/{dashboard_id}', headers=headers)
    assert rv.status_code == 400

    data = {
        'title': 'Updated dashboard',
        'is_public': True
    }
    rv = client.patch(
        f'/dashboards/{dashboard_id}', headers=headers, json=data)
    assert rv.status_code == 200
    with current_app.app_context():
        d = Dashboard.query.get(dashboard_id)
        assert d.title == data['title']
        assert d.is_public == data['is_public']


def test_post_dashboard_missing_data(client):
    headers = {'X-Auth-Token': str(client.secret)}

    # Missing data
    data = {
        'title': 'Updated dashboard',
    }
    rv = client.post('/dashboards', headers=headers, json=data)
    assert rv.status_code == 400
    assert rv.json['status'] == 'ERROR'
    assert rv.json['message'] == 'Validation error'


def test_post_dashboard_success(client):
    headers = {'X-Auth-Token': str(client.secret)}

    data = {
        'title': 'Updated dashboard',
        'is_public': True,
        'task_id': 'test',
        'job_id': 1000,
        'workflow_id': 25,
        'user_id': 1, 'user_name': 'demo', 'user_login': 'demo',
        'user': {
            'id': 1, 'name': 'demo', 'login': 'demo'
        },
        'visualizations': [
            {
                'task_id': 'abcde',
                'title': 'Visualization',
                'type': {
                    'id': 131
                }
            }
        ]
    }
    rv = client.post('/dashboards', headers=headers, json=data)
    assert rv.status_code == 200, rv.json
    with current_app.app_context():
        dashboard = Dashboard.query.get(rv.json['id'])
        assert dashboard is not None
        for k, v in data.items():
            if k not in ('visualizations', 'user'):
                assert getattr(dashboard, k) == v

