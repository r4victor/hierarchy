import pytest

from app.db import get_db_conn
from app.models import Node

from tests.test_data import populate_table_with_example_rows, example_tree


def test_root_node(app):
    expected_root_node = Node(id=1, name='root', parent_id=None, lft=0, rgt=1)
    with app.app_context():
        root_node = Node.get_by_id(1)
    
    assert root_node == expected_root_node


def test_create_node(app):
    expected_root_node = Node(id=1, name='root', parent_id=None, lft=0, rgt=3)
    expected_new_node = Node(id=2, name='new node', parent_id=1, lft=1, rgt=2, tree_id=2)
    with app.app_context():
        new_node = Node.create(expected_new_node.name, Node.get_by_id(expected_new_node.parent_id))
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
        Node.get_by_id(5).move(Node.get_by_id(2))
        tree = Node.get_by_id(1).get_subtree()
    
    assert tree['children'] == example_tree['children']


@pytest.mark.parametrize(
    'name', ['Simple', 'немного harder', '234 234 444 ', 'path/to/something', 'try_underscores__']
)
def test_name_validation_valid(name):
    try:
        Node.validate_name(name)
    except ValueError:
        pytest.fail()


@pytest.mark.parametrize(
    'name', ['', ' ', '\t', '  ', ' 123', 're  re', '😀']
)
def test_name_validation_invalid(name):
    with pytest.raises(ValueError):
        Node.validate_name(name)


def test_name_uniqueness_fail(app):
    with app.app_context():
        node = Node.create('Unique', Node.get_by_id(Node.get_root_id()))
        with pytest.raises(ValueError):
                Node.create('Unique', node)


def test_name_uniqueness_accept(app):
    with app.app_context():
        Node.create('Unique', Node.get_by_id(Node.get_root_id()))
        try:
            Node.create('Unique', Node.get_by_id(Node.get_root_id()))
        except ValueError:
            pytest.fail()

        