from .fixtures import *
from flask import current_app


def test_get_visualizations_unauthorized(client):
    rv = client.get('/visualizations', headers=None)

    assert rv.json['message'] == 'The method is not allowed '\
                                 'for the requested URL.'
    assert rv.status_code == 405

    rv = client.get('/visualizations/0/0/1', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401

    rv = client.post('/visualizations', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401

    rv = client.patch('/visualizations/0/01', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401

    rv = client.delete('/visualizations/0/0/1', headers=None)
    assert rv.json['status'] == 'ERROR'
    assert rv.status_code == 401


def test_get_visualization_return_none(client):
    headers = {'X-Auth-Token': str(client.secret)}

    rv = client.get('/visualizations/2/2/200', headers=headers)
    assert rv.status_code == 404
    assert rv.json['status'] == 'ERROR', rv.json['status']


def test_get_visualization(client):
    headers = {'X-Auth-Token': str(client.secret)}
    vis_id = 3
    task_id = 1
    job_id = 1
    rv = client.get(
        f'/visualizations/{job_id}/{task_id}/{vis_id}?fields=title,data',
        headers=headers)

    # Old style API. Change it in future
    v3 = rv.json
    assert v3['title'] == 'Third visualization'
    assert set(v3.keys()) == {'job_id', 'data',
                              'task_id', 'type', 'title', 'id'}
    assert rv.status_code == 200
