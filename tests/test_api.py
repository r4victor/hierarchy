import pytest

from tests.test_data import example_hierarchy


def test_create_item(client, app, example_hierarchy):
    response = client.post('/item', json={'name': 'test item', 'parent_id': None})
    assert response.status_code == 201
    assert response.headers['Location']


def test_replace_item(client, app, example_hierarchy):
    updated_item = {'id': 5, 'name': 'test item', 'parent_id': 3}
    response = client.put('/item', json=updated_item)
    assert response.get_json() == updated_item


def test_get_item(client, app, example_hierarchy):
    response = client.get('/item/2')
    data = response.get_json()
    item = example_hierarchy[0]
    assert data == {
        'id': item['id'],
        'name': item['name'],
        'parent_id': item['parent_id']
    }


def test_update_item(client, app):
    response = client.post('/item', json={'name': 'test item', 'parent_id': None})
    assert response.status_code == 201
    item = client.get(response.headers['Location']).get_json()
    updated_item = client.patch(f'/item/{item["id"]}', json={'name': 'new name'}).get_json()
    assert updated_item == {
        'id': item['id'],
        'name': 'new name',
        'parent_id': item['parent_id']
    }
