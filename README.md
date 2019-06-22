
# Hierarchy

## Overview

This service provides an API for working with a set of items by forming an hierarchy. Hierarchy is represented by a collection of trees.
Each item within a tree has a unique name and points to its parent ( which is 'null' in case of a root item).
One can create, rename, move and delete items within the hierarchy.

See OpenAPI specification: [app.swaggerhub.com](https://app.swaggerhub.com/apis-docs/r4victor/Hierarchy/0.1.0#/)

## Usage

### Setup

1. Build image: `docker-compose build`
2. Initialize database: `docker-compose run --service-ports web flask init-db`

### Running

3. `docker-compose up -d`

## Implementation details

Implementation of hierarchical structure is based on [nested sets model](https://en.wikipedia.org/wiki/Nested_set_model).

