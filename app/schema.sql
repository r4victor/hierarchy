DROP TABLE IF EXISTS node;

CREATE TABLE node (
    id SERIAL PRIMARY KEY,
    parent_id INTEGER,
    name TEXT NOT NULL,
    lft INTEGER NOT NULL,
    rgt INTEGER NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES node (id)
);