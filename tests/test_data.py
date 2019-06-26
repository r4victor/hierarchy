import pytest

from app.db import get_db_conn


@pytest.fixture
def example_hierarchy(app):
    values = [
        ('level1-1', 1, 1, 6, 2),
        ('level2-1', 2, 2, 3, 2),
        ('level2-2', 2, 4, 5, 2),
        ('level1-2', 1, 7, 10, 5),
        ('level2-3', 5, 8, 9, 5),
        ('level1-3', 1, 11, 12, 7),
    ]
    with app.app_context():
        with get_db_conn().cursor() as cur:
            for t in values:
                cur.execute('INSERT INTO node (name, parent_id, lft, rgt, tree_id) VALUES (%s, %s, %s, %s, %s)', t)
            cur.execute('UPDATE node SET rgt = 13 WHERE id = 1')
        get_db_conn().commit()

    return [
        {
            'id': 2,
            'name': 'level1-1',
            'parent_id': None,
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
            'parent_id': None,
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
            'parent_id': None,
            'children': []
        }
    ]