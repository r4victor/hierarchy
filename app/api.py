from flask import Blueprint, request, abort, jsonify, url_for, make_response

from app.models import Node


bp = Blueprint('api', __name__)


def api_message(status, message):
    return make_response(jsonify(message=message)), status


@bp.errorhandler(404)
def not_found_error(e):
    return api_message(404, 'Not found')


@bp.route('/item', methods=('POST', 'PUT'))
def item():
    data = request.get_json()
    if request.method == 'POST':
        if 'name' not in data:
            return api_message(400, '"name" required')

        if 'parent_id' not in data:
            return api_message(400, '"parent_id" required')

        parent_id = data['parent_id']
        if parent_id is None:
            parent_id = Node.get_root_id()

        parent_node = Node.get_by_id(parent_id)
        if parent_node is None:
            return api_message(400, 'Invalid "parent_id"')

        try:
            node = Node.create(name=data['name'], parent_node=parent_node)
        except ValueError as e:
            return api_message(400, str(e))
        
        return '', 201, {'Location': url_for('.item_by_id', item_id=node.id)}
    
    if request.method == 'PUT':
        if 'id' not in data:
            return api_message(400, '"id" required')

        node = Node.get_by_id(data['id'])
        if node is None:
            return api_message(404, 'Item not found')

        if 'name' not in data:
            return api_message(400, '"name" required')

        if 'parent_id' not in data:
            return api_message(400, '"parent_id reqired"')
    
        if data['name'] != node.name:
            try:
                node = node.rename(data['name'])
            except ValueError as e:
                return api_message(400, str(e))

        parent_id = data['parent_id']
        if parent_id is None:
            parent_id = Node.get_root_id()
        
        if parent_id != node.parent_id:
            parent_node = Node.get_by_id(parent_id)
            if parent_node is None:
                return api_message(400, 'Parent item not found')

            try:
                node = node.move(parent_node)
            except ValueError as e:
                return api_message(400, str(e))

        return jsonify(node.to_item())


@bp.route('/item/<int:item_id>', methods=('GET', 'PATCH', 'DELETE'))
def item_by_id(item_id):
    # disallow direct access to the root node
    if item_id == Node.get_root_id():
        abort(404)

    node = Node.get_by_id(item_id)
    if node is None:
        abort(404)

    if request.method == 'GET':
        return jsonify(node.to_item())
    
    if request.method == 'DELETE':
        node.delete()
        return '', 204

    if request.method == 'PATCH':
        data = request.get_json()

        node = Node.get_by_id(item_id)
        if node is None:
            return api_message(404, 'Item not found')
    
        if 'name' in data and data['name'] != node.name:
            try:
                node = node.rename(data['name'])
            except ValueError as e:
                return api_message(400, str(e))
        
        if 'parent_id' in data:
            parent_id = data['parent_id']
            if parent_id is None:
                parent_id = Node.get_root_id()

            if parent_id != node.parent_id:
                parent_node = Node.get_by_id(parent_id)
                if parent_node is None:
                    return api_message(404, 'Parent item not found')

                try:
                    node = node.move(parent_node)
                except ValueError as e:
                    return api_message(400, str(e))
        
        return jsonify(node.to_item())


@bp.route('/hierarchy', methods=('GET',))
def hierarchy():
    return jsonify(Node.get_by_id(Node.get_root_id()).get_subtree()['children'])


@bp.route('/subtree/<int:root_item_id>', methods=('GET',))
def subtree(root_item_id):
    # disallow direct access to the root node
    if root_item_id == Node.get_root_id():
        abort(404)

    node = Node.get_by_id(root_item_id)
    if node is None:
        abort(404)
        
    return jsonify(node.get_subtree())
