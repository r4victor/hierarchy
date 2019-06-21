import pytest

from app.db import get_db_conn
from app.models import Node


@pytest.fixture
def example_tree():
    return {
        'id': 1,
        'name': 'root',
        'parent_id': None,
        'children': [
            {
                'id': 2,
                'name': 'level1-1',
                'parent_id': 1,
                'children': [
                    {
                        'id': 3,
                        'name': 'level2-1',
                        'parent_id': 2,
                        'children': []
                    },
                    {
                        'id': 4,
                        'name': 'level2-2',
                        'parent_id': 2,
                        'children': []
                    }
                ]
            },
            {
                'id': 5,
                'name': 'level1-2',
                'parent_id': 1,
                'children': [
                    {
                        'id': 6,
                        'name': 'level2-3',
                        'parent_id': 5,
                        'children': []
                    }
                ]
            },
            {
                'id': 7,
                'name': 'level1-3',
                'parent_id': 1,
                'children': []
            }
        ]
    }


def populate_table_with_example_rows():
    values = [
        ('level1-1', 1, 1, 6),
        ('level2-1', 2, 2, 3),
        ('level2-2', 2, 4, 5),
        ('level1-2', 1, 7, 10),
        ('level2-3', 5, 8, 9),
        ('level1-3', 1, 11, 12),
    ]
    with get_db_conn().cursor() as cur:
        for t in values:
            cur.execute('INSERT INTO node (name, parent_id, lft, rgt) VALUES (%s, %s, %s, %s)', t)
        cur.execute('UPDATE node SET rgt = 13 WHERE id = 1')
    get_db_conn().commit()


def test_root_node(app):
    expected_root_node = Node(id=1, name='root', parent_id=None, lft=0, rgt=1)
    with app.app_context():
        root_node = Node.get_by_id(1)
    
    assert root_node == expected_root_node


def test_create_node(app):
    expected_root_node = Node(id=1, name='root', parent_id=None, lft=0, rgt=3)
    expected_new_node = Node(id=2, name='new node', parent_id=1, lft=1, rgt=2)
    with app.app_context():
        new_node = Node.create(expected_new_node.name, expected_new_node.parent_id)
        assert new_node == Node.get_by_id(expected_new_node.id)
        root_node = Node.get_by_id(expected_root_node.id)

    assert root_node == expected_root_node and new_node == expected_new_node


def test_get_subtree(app, example_tree):
    with app.app_context():
        populate_table_with_example_rows()
        node = Node.get_by_id(1)
        subtree = node.get_subtree()
    assert subtree == example_tree


def test_delete_node(app, example_tree):
    del example_tree['children'][1]
    with app.app_context():
        populate_table_with_example_rows()
        Node.get_by_id(5).delete()
        tree = Node.get_by_id(1).get_subtree()
    assert tree == example_tree


def test_move(app, example_tree):
    subtree = example_tree['children'].pop(1)
    subtree['parent_id'] = 2
    example_tree['children'][0]['children'].append(subtree)
    with app.app_context():
        populate_table_with_example_rows()
        Node.get_by_id(5).move(2)
        tree = Node.get_by_id(1).get_subtree()
    assert tree == example_tree

        