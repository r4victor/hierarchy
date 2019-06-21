from dataclasses import dataclass, replace

from app.db import get_db_conn


@dataclass(frozen=True)
class Node:
    id: int
    name: str
    parent_id: int
    lft: int
    rgt: int

    @classmethod
    def _from_dict_cursor_result(cls, res):
        return cls(**res)

    @classmethod
    def get_by_id(cls, id):
        with get_db_conn().cursor() as cur:
            cur.execute('SELECT * FROM node WHERE id=%s', (id,))
            res = cur.fetchone()
        return cls(**res)

    @classmethod
    def create(cls, name, parent_id):
        parent_node = cls.get_by_id(parent_id)
        values = (name, parent_id, parent_node.rgt, parent_node.rgt + 1)
        with get_db_conn().cursor() as cur:
            cur.execute('UPDATE node SET rgt = rgt + 2 WHERE rgt >= %s', (parent_node.rgt,))
            cur.execute('UPDATE node SET lft = lft + 2 WHERE lft > %s', (parent_node.rgt,))
            cur.execute('INSERT INTO node (name, parent_id, lft, rgt) VALUES (%s, %s, %s, %s) RETURNING id', values)
            node_id = cur.fetchone()[0]
        get_db_conn().commit()
        return cls(node_id, *values)

    def rename(self, new_name):
        with get_db_conn().cursor() as cur:
            cur.execute('UPDATE node SET name = %s WHERE id = %s', (new_name, self.id))
        get_db_conn().commit()
        return replace(self, name=new_name)

    def move(self, parent_id):
        parent_node = self.get_by_id(parent_id)
        if self.lft < parent_node.lft < self.rgt:
            raise ValueError('Cannot move under a child')
        with get_db_conn().cursor() as cur:
            cur.execute('UPDATE node SET parent_id = %s WHERE id = %s', (parent_id, self.id))
            # temporary remove subtree
            cur.execute('UPDATE node SET lft = -lft, rgt = -rgt WHERE lft BETWEEN %s AND %s', (self.lft, self.rgt))

            cur.execute('UPDATE node SET rgt = rgt - %s WHERE lft > %s', (self._diff, self.rgt))
            cur.execute('UPDATE node SET lft = lft - %s WHERE lft > %s', (self._diff, self.rgt))

            cur.execute('UPDATE node SET rgt = rgt + %s WHERE lft > %s', (self._diff, parent_node.rgt))
            cur.execute('UPDATE node SET lft = lft + %s WHERE lft > %s', (self._diff, parent_node.rgt))

            cur.execute('UPDATE node SET rgt = rgt + %s WHERE id = %s', (self._diff, parent_id))
            cur.execute(
                'UPDATE node SET lft = - lft + %s, rgt = - rgt + %s WHERE lft BETWEEN %s AND %s',
                (parent_node.rgt - self.lft, parent_node.rgt - self.lft, -self.rgt, -self.lft)
            )
        get_db_conn().commit()

    @property
    def _diff(self):
        return self.rgt - self.lft + 1

    def delete(self):
        with get_db_conn().cursor() as cur:
            cur.execute('DELETE FROM node WHERE lft BETWEEN %s AND %s', (self.lft, self.rgt))
            cur.execute('UPDATE node SET lft = lft - %s WHERE lft > %s', (self._diff, self.rgt))
            cur.execute('UPDATE node SET rgt = rgt - %s WHERE rgt > %s', (self._diff, self.rgt))
        get_db_conn().commit()

    def _get_subtree_rows(self):
        with get_db_conn().cursor() as cur:
            cur.execute(
                    'SELECT * FROM node WHERE lft >= %s and rgt <= %s ORDER BY lft ASC',
                    (self.lft, self.rgt)
            )
            res = cur.fetchall()
        print(res)
        return res

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
                'parent_id': row['parent_id'],
                'children': children[i]
            })

            stack.append((row['rgt'], parent_index))
            parent_index = i

        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'children': children[0]
        }


