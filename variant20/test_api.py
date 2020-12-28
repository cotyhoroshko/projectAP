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


def test_unauthorized_get_adv(client):
    resp = client.get('/advertisements')
    data = resp.get_json()
    local_count = len(list(filter(lambda x: x['modifier'] == 'local', data)))
    assert local_count == 0
    assert len(data) == 3
    assert resp.status_code == 200


def test_authorized_get_adv(client):
    credentials = b64encode(b'alice@testmail.ua:pass456').decode('utf-8')
    resp = client.get('/advertisements',
                      headers={'Authorization': f'Basic {credentials}'})
    data = resp.get_json()
    assert len(data) == 5
    assert resp.status_code == 200


def test_user_id_of_ad(client):
    resp = client.get('/advertisements')
    data = resp.get_json()
    selected_ad: dict = list(filter(lambda x: x['summary'] == 's1', data))[0]
    users_resp = client.get('/users')
    user_data = users_resp.get_json()
    creator_id = list(filter(lambda x: x['name'] == 'alice', user_data))[
        0]['id']

    assert selected_ad['user_id'] == creator_id


def test_put_non_author(client):
    credentials = b64encode(b'jane@testmail.ua:pass789').decode('utf-8')
    users = client.get('/users').get_json()
    alice_id = list(filter(lambda x: x['name'] == 'alice', users))[0]['id']
    ads = client.get('/advertisements').get_json()
    alice_ad: dict = list(filter(lambda x: x['user_id'] == alice_id, ads))[0]
    ad_topic = alice_ad['topic']
    ad_id = alice_ad['id']

    resp = client.put(f'/advertisements/{ad_topic}/{ad_id}',
                      content_type='application/json',
                      headers={'Authorization': f'Basic {credentials}'},
                      data=json.dumps({'summary': 'summary555'}))

    assert resp.status_code == 403


def test_put_anonymous(client):
    users = client.get('/users').get_json()
    alice_id = list(filter(lambda x: x['name'] == 'alice', users))[0]['id']
    ads = client.get('/advertisements').get_json()
    alice_ad: dict = list(filter(lambda x: x['user_id'] == alice_id, ads))[0]
    ad_topic = alice_ad['topic']
    ad_id = alice_ad['id']

    resp = client.put(f'/advertisements/{ad_topic}/{ad_id}',
                      content_type='application/json',
                      data=json.dumps({'summary': 'summary555'}))

    assert resp.status_code == 403


def test_put_author(client):
    credentials = b64encode(b'alice@testmail.ua:pass456').decode('utf-8')
    users = client.get('/users').get_json()
    alice_id = list(filter(lambda x: x['name'] == 'alice', users))[0]['id']
    ads = client.get('/advertisements').get_json()
    alice_ad: dict = list(filter(lambda x: x['user_id'] == alice_id, ads))[0]
    ad_topic = alice_ad['topic']
    ad_id = alice_ad['id']

    resp = client.put(f'/advertisements/{ad_topic}/{ad_id}',
                      content_type='application/json',
                      headers={'Authorization': f'Basic {credentials}'},
                      data=json.dumps({'summary': 'summary555'}))

    resp_data = resp.get_json()

    assert resp.status_code == 201
    assert resp_data['summary'] == 'summary555'


def test_put_master(client):
    credentials = b64encode(b'bob@testmail.ua:pass123').decode('utf-8')
    users = client.get('/users').get_json()
    alice_id = list(filter(lambda x: x['name'] == 'alice', users))[0]['id']
    ads = client.get('/advertisements').get_json()
    alice_ad: dict = list(filter(lambda x: x['user_id'] == alice_id, ads))[0]
    ad_topic = alice_ad['topic']
    ad_id = alice_ad['id']

    resp = client.put(f'/advertisements/{ad_topic}/{ad_id}',
                      content_type='application/json',
                      headers={'Authorization': f'Basic {credentials}'},
                      data=json.dumps({'summary': 'summary555'}))

    resp_data = resp.get_json()

    assert resp.status_code == 201
    assert resp_data['summary'] == 'summary555'


def test_delete_non_author(client):
    credentials = b64encode(b'jane@testmail.ua:pass789').decode('utf-8')
    users = client.get('/users').get_json()
    alice_id = list(filter(lambda x: x['name'] == 'alice', users))[0]['id']
    ads = client.get('/advertisements').get_json()
    alice_ad: dict = list(filter(lambda x: x['user_id'] == alice_id, ads))[0]
    ad_topic = alice_ad['topic']
    ad_id = alice_ad['id']

    resp = client.delete(f'/advertisements/{ad_topic}/{ad_id}',
                         headers={'Authorization': f'Basic {credentials}'})

    assert resp.status_code == 403


def test_delete_anonymous(client):
    users = client.get('/users').get_json()
    alice_id = list(filter(lambda x: x['name'] == 'alice', users))[0]['id']
    ads = client.get('/advertisements').get_json()
    alice_ad: dict = list(filter(lambda x: x['user_id'] == alice_id, ads))[0]
    ad_topic = alice_ad['topic']
    ad_id = alice_ad['id']

    resp = client.delete(f'/advertisements/{ad_topic}/{ad_id}')

    assert resp.status_code == 403


def test_delete_author(client):
    credentials = b64encode(b'alice@testmail.ua:pass456').decode('utf-8')
    users = client.get('/users').get_json()
    alice_id = list(filter(lambda x: x['name'] == 'alice', users))[0]['id']
    ads = client.get('/advertisements').get_json()
    ads_before = len(ads)
    alice_ad: dict = list(filter(lambda x: x['user_id'] == alice_id, ads))[0]
    ad_topic = alice_ad['topic']
    ad_id = alice_ad['id']

    client.delete(f'/advertisements/{ad_topic}/{ad_id}',
                  headers={'Authorization': f'Basic {credentials}'})

    ads_after = len(client.get('/advertisements').get_json())

    assert ads_after == ads_before - 1


def test_anon_post(client):
    resp = client.post('/advertisements', content_type='application/json',
                       data=json.dumps({'summary': 'summ123', 'description': 'desc123',
                                        'topic': 'topic123', 'modifier': 'public'}))

    assert resp.status_code == 403


def test_get_by_id(client):
    credentials = b64encode(b'alice@testmail.ua:pass456').decode('utf-8')
    req_data = {'summary': 's123', 'description': 'desc123',
                'topic': 'topic123', 'modifier': 'public'}
    auth_id = list(filter(lambda x: x['name'] == 'alice', client.get(
        '/users').get_json()))[0]['id']

    post_resp = client.post('/advertisements', content_type='application/json',
                            data=json.dumps(req_data), headers={'Authorization': f'Basic {credentials}'})
    post_data = post_resp.get_json()
    ad_topic = req_data['topic']
    ad_id = post_data['id']

    get_resp = client.get(f'/advertisements/{ad_topic}/{ad_id}')
    get_data = get_resp.get_json()

    assert post_data == get_data
    assert get_data['user_id'] == auth_id
