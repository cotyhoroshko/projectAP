from variant20.app import create_app
from flask import json
import pytest
from base64 import b64encode


def seed_users(client):
    client.post('/users', data=json.dumps({'name': 'bob', 'role': 'master',
                                           'email': 'bob@testmail.ua', 'password_hash': 'pass123'}),
                content_type='application/json')

    client.post('/users', data=json.dumps({'name': 'alice', 'role': 'average',
                                           'email': 'alice@testmail.ua', 'password_hash': 'pass456'}),
                content_type='application/json')

    client.post('/users', data=json.dumps({'name': 'jane', 'role': 'average',
                                           'email': 'jane@testmail.ua', 'password_hash': 'pass789'}),
                content_type='application/json')


def seed_ads(client):
    alice_credentials = b64encode(b'alice@testmail.ua:pass456').decode('utf-8')
    jane_credentials = b64encode(b'jane@testmail.ua:pass789').decode('utf-8')

    client.post('/advertisements', content_type='application/json',
                headers={'Authorization': f'Basic {alice_credentials}'},
                data=json.dumps({'summary': 's1', 'description': 'desc1', 'topic': 'topic1', 'modifier': 'public'}))

    client.post('/advertisements', content_type='application/json',
                headers={'Authorization': f'Basic {alice_credentials}'},
                data=json.dumps({'summary': 's2', 'description': 'desc2', 'topic': 'topic2', 'modifier': 'local'}))

    client.post('/advertisements', content_type='application/json',
                headers={'Authorization': f'Basic {alice_credentials}'},
                data=json.dumps({'summary': 's3', 'description': 'desc3', 'topic': 'topic1', 'modifier': 'public'}))

    client.post('/advertisements', content_type='application/json',
                headers={'Authorization': f'Basic {jane_credentials}'},
                data=json.dumps({'summary': 's4', 'description': 'desc4', 'topic': 'topic3', 'modifier': 'public'}))

    client.post('/advertisements', content_type='application/json',
                headers={'Authorization': f'Basic {jane_credentials}'},
                data=json.dumps({'summary': 's5', 'description': 'desc5', 'topic': 'topic1', 'modifier': 'local'}))


@pytest.fixture
def client():
    app = create_app(True)
    client = app.test_client()
    seed_users(client)
    seed_ads(client)
    return client
