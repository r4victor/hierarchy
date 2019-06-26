import re, string
from dataclasses import dataclass, replace

import psycopg2.errors

from app.db import get_db_conn


@dataclass(frozen=True)
class Node:
    """
    Tree structure based on nested set model: https://en.wikipedia.org/wiki/Nested_set_model.
    Collection of trees represented by one tree with a fictional root node.
    """
    id: int
    name: str
    parent_id: int
    lft: int
    rgt: int
    tree_id: int = None

    @staticmethod
    def get_root_id():
        return 1

    @classmethod
    def get_root_node(cls):
        return cls.get_by_id(cls.get_root_id())

    @staticmethod
    def validate_name(name):
        if name == '':
            raise ValueError('Name should not be empty')
        if name.startswith(' '):
            raise ValueError('Name should not start with a space')
        if re.fullmatch(r'([\wЁёА-я/\\]+ |[\wЁёА-я/\\]+)+', name, re.ASCII) is None:
            raise ValueError(
                'Name should contain only latin or cyrillic symbols, ' \
                "digits, single spaces or any of: '_', '/', '\\'"
            )

    @classmethod
    def get_by_id(cls, id):
        with get_db_conn().cursor() as cur:
            cur.execute('SELECT * FROM node WHERE id=%s', (id,))
            res = cur.fetchone()
        if res is None:
            return None
        return cls(**res)
    
    def to_item(self):
        return {
            'id': self.id,
            'name': self.name,
            # hide root node
            'parent_id': self.parent_id if self.parent_id != self.get_root_id() else None
        }

    @classmethod
    def create(cls, name, parent_node):
        cls.validate_name(name)
        tree_id = parent_node.tree_id
        with get_db_conn().cursor() as cur:
            cur.execute('UPDATE node SET rgt = rgt + 2 WHERE rgt >= %s', (parent_node.rgt,))
            cur.execute('UPDATE node SET lft = lft + 2 WHERE lft > %s', (parent_node.rgt,))
            try:
                cur.execute(
                    'INSERT INTO node (name, parent_id, lft, rgt, tree_id) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                    (name, parent_node.id, parent_node.rgt, parent_node.rgt + 1, tree_id)
                )
            except psycopg2.errors.UniqueViolation:
                raise ValueError('Names should be unique within a tree')
            node_id = cur.fetchone()[0]
            if tree_id is None:
                cur.execute('UPDATE node SET tree_id = %s WHERE id = %s', (node_id, node_id,))
                tree_id = node_id
        get_db_conn().commit()
        return cls(node_id, name, parent_node.id, parent_node.rgt, parent_node.rgt + 1, tree_id)

    def rename(self, new_name):
        self.validate_name(new_name)
        with get_db_conn().cursor() as cur:
            try:
                cur.execute('UPDATE node SET name = %s WHERE id = %s', (new_name, self.id))
            except psycopg2.errors.UniqueViolation:
                raise ValueError('Names should be unique within a tree')
        get_db_conn().commit()
        return replace(self, name=new_name)
    
    def delete(self):
        with get_db_conn().cursor() as cur:
            cur.execute('DELETE FROM node WHERE lft BETWEEN %s AND %s', (self.lft, self.rgt))
            cur.execute('UPDATE node SET lft = lft - %s WHERE lft > %s', (self._diff, self.rgt))
            cur.execute('UPDATE node SET rgt = rgt - %s WHERE rgt > %s', (self._diff, self.rgt))
        get_db_conn().commit()

    @property
    def _diff(self):
        return self.rgt - self.lft + 1

    def move(self, parent_node):
        if self.id == parent_node.id:
            raise ValueError('Cannot move under itself')
        
        if self.lft < parent_node.lft < self.rgt:
            raise ValueError('Cannot move under a child')

        tree_id = parent_node.tree_id
        if tree_id is None:
            tree_id = self.id

        with get_db_conn().cursor() as cur:
            cur.execute('UPDATE node SET parent_id = %s WHERE id = %s', (parent_node.id, self.id))
            # temporary remove subtree, update tree_id
            try:
                cur.execute(
                    'UPDATE node SET tree_id = %s, lft = -lft, rgt = -rgt WHERE lft BETWEEN %s AND %s',
                    (tree_id, self.lft, self.rgt)
                )
            except psycopg2.errors.UniqueViolation:
                raise ValueError('Names should be unique within a tree')
            # shift right
            cur.execute('UPDATE node SET rgt = rgt + %s WHERE rgt >= %s', (self._diff, parent_node.rgt))
            cur.execute('UPDATE node SET lft = lft + %s WHERE lft > %s', (self._diff, parent_node.rgt))
            # place subtree
            cur.execute(
                'UPDATE node SET lft = - lft + %s, rgt = - rgt + %s WHERE lft BETWEEN %s AND %s',
                (parent_node.rgt - self.lft, parent_node.rgt - self.lft, -self.rgt, -self.lft)
            )
            # shift left
            cur.execute('UPDATE node SET rgt = rgt - %s WHERE rgt > %s', (self._diff, self.rgt))
            cur.execute('UPDATE node SET lft = lft - %s WHERE lft > %s', (self._diff, self.rgt))

        get_db_conn().commit()
        return replace(self, parent_id=parent_node.id, tree_id=tree_id)

    def get_subtree(self):
        subtree_rows = self._get_subtree_rows()
        children = [[] for _ in range(len(subtree_rows))]
        parent_index = 0
        # track previous parent_index
        stack = [(self.rgt, None)]
        for i, row in enumerate(self._get_subtree_rows()[1:], 1):
            while row['rgt'] > stack[-1][0]:
                # level up
                _, parent_index = stack.pop()
            
            children[parent_index].append({
                'id': row['id'],
                'name': row['name'],
                'parent_id': row['parent_id'] if row['parent_id'] != self.get_root_id() else None,
                'children': children[i]
            })

            stack.append((row['rgt'], parent_index))
            parent_index = i

        return {
            **self.to_item(),
            'children': children[0]
        }
    
    def _get_subtree_rows(self):
        with get_db_conn().cursor() as cur:
            cur.execute(
                    'SELECT * FROM node WHERE lft >= %s and rgt <= %s ORDER BY lft ASC',
                    (self.lft, self.rgt)
            )
            res = cur.fetchall()
        return res

    @classmethod
    def get_hierarchy(cls):
        return cls.get_root_node().get_subtree()['children']