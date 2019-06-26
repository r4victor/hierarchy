import pytest

from app.db import get_db_conn
from app.models import Node

from tests.test_data import example_hierarchy


def test_get_root_node(app):
    expected_root_node = Node(id=1, name='root', parent_id=None, lft=0, rgt=1)
    with app.app_context():
        root_node = Node.get_root_node()
    
    assert root_node == expected_root_node


def test_get_hierarchy(app, example_hierarchy):
    with app.app_context():
        hierarchy = Node.get_hierarchy()
    assert hierarchy == example_hierarchy


def test_delete_node(app, example_hierarchy):
    del example_hierarchy[1]
    with app.app_context():
        Node.get_by_id(5).delete()
        hierarchy = Node.get_hierarchy()
    assert hierarchy == example_hierarchy


class TestNameValidation:
    @pytest.mark.parametrize(
        'name', ['Simple', 'немного harder', '234 234 444 ', 'path/to/something', 'try_underscores__']
    )
    def test_name_validation_valid(self, name):
        try:
            Node.validate_name(name)
        except ValueError:
            pytest.fail()


    @pytest.mark.parametrize(
        'name', ['', ' ', '\t', '  ', ' 123', 're  re', '😀']
    )
    def test_name_validation_invalid(self, name):
        with pytest.raises(ValueError):
            Node.validate_name(name)


class TestCreateNode:
    def test_create_node(self, app):
        expected_root_node = Node(id=1, name='root', parent_id=None, lft=0, rgt=3)
        expected_new_node = Node(id=2, name='new node', parent_id=1, lft=1, rgt=2, tree_id=2)
        with app.app_context():
            new_node = Node.create(expected_new_node.name, Node.get_by_id(expected_new_node.parent_id))
            assert new_node == Node.get_by_id(expected_new_node.id)
            root_node = Node.get_by_id(expected_root_node.id)

        assert root_node == expected_root_node and new_node == expected_new_node

    def test_name_uniqueness_fail(self, app):
        with app.app_context():
            node = Node.create('Unique', Node.get_root_node())
            with pytest.raises(ValueError):
                    Node.create('Unique', node)

    def test_name_uniqueness_accept(self, app):
        with app.app_context():
            Node.create('Unique', Node.get_root_node())
            try:
                Node.create('Unique', Node.get_root_node())
            except ValueError:
                pytest.fail()


class TestMove:
    def test_move_rigth(self, app, example_hierarchy):
        item = example_hierarchy[0]['children'].pop(0)
        item['parent_id'] = 7
        example_hierarchy[2]['children'].append(item)
        with app.app_context():
            Node.get_by_id(3).move(Node.get_by_id(7))
            hierarchy = Node.get_hierarchy()
        
        assert hierarchy == example_hierarchy

    def test_move_subtree(self, app, example_hierarchy):
        subtree = example_hierarchy.pop(1)
        subtree['parent_id'] = 2
        example_hierarchy[0]['children'].append(subtree)
        with app.app_context():
            Node.get_by_id(5).move(Node.get_by_id(2))
            hierarchy = Node.get_hierarchy()
        
        assert hierarchy == example_hierarchy

    def test_move_under_itself(self, app, example_hierarchy):
        with app.app_context():
            with pytest.raises(ValueError):
                Node.get_by_id(3).move(Node.get_by_id(3))

    def test_move_under_child(self, app, example_hierarchy):
        with app.app_context():
            with pytest.raises(ValueError):
                Node.get_by_id(2).move(Node.get_by_id(3))
    
    def test_keep_name_unique(self, app, example_hierarchy):
        with app.app_context():
            node3 = Node.get_by_id(3)
            node7 = Node.get_by_id(7)
            Node.create(name='I am unique within my tree', parent_node=node3)
            Node.create(name='I am unique within my tree', parent_node=node7)
            with pytest.raises(ValueError):
                node3.move(node7)


        