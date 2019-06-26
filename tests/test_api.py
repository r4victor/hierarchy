import pytest

from app.models import Node

from tests.test_data import example_hierarchy


def test_get_item(client, app, example_hierarchy):
    data = client.get('/item/2').get_json()
    item = example_hierarchy[0]
    assert data == {
        'id': item['id'],
        'name': item['name'],
        'parent_id': item['parent_id']
    }


def test_create_item(client, app, example_hierarchy):
    item_data = {'name': 'test item', 'parent_id': None}
    response = client.post('/item', json={'name': 'test item', 'parent_id': None})
    assert response.status_code == 201
    data = client.get(response.headers['Location']).get_json()
    assert data['name'] == item_data['name'] and data['parent_id'] == item_data['parent_id']


def test_get_hierarchy(client, app, example_hierarchy):
    assert client.get('/hierarchy').get_json() == example_hierarchy


def test_get_subtree(client, app, example_hierarchy):
    assert client.get('/subtree/2').get_json() == example_hierarchy[0]


class TestUpdateItem:
    def test_update_name(self, client, app):
        with app.app_context():
            node = Node.create(name='old name', parent_node=Node.get_root_node())
        updated_item = client.post(f'/item/{node.id}', json={'name': 'new name'}).get_json()
        assert updated_item == client.get(f'/item/{node.id}').get_json()
        assert updated_item == {
            'id': node.id,
            'name': 'new name',
            'parent_id': None
        }

    def test_update_parent(self, client, example_hierarchy):
        item = example_hierarchy[0]['children'][1]
        updated_item = client.post(f'/item/{item["id"]}', json={'parent_id': 6}).get_json()
        assert updated_item == {
            'id': item["id"],
            'name': item["name"],
            'parent_id': 6
        }


def test_delete_item(client, example_hierarchy):
    item = example_hierarchy[0]['children'].pop(1)
    client.delete(f'/item/{item["id"]}')
    assert client.get('/hierarchy').get_json() == example_hierarchy
