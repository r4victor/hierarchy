from flask import Blueprint, request, abort, jsonify, url_for, make_response

from app.models import Node


bp = Blueprint('api', __name__)


def api_message(status, message):
    return make_response(jsonify(status=status, message=message)), status


@bp.errorhandler(404)
def not_found_error(e):
    return api_message(404, 'Not found')


@bp.route('/item', methods=('POST', 'PUT'))
def item():
    data = request.get_json()
    if request.method == 'POST':
        if 'name' not in data:
            return api_message(400, 'Name required')

        parent_id = data.get('parent_id', Node.get_root_id())
        parent_node = Node.get_by_id(parent_id)
        if parent_node is None:
            return api_message(400, 'Invalid parent_id')
    
        node = Node.create(name=data['name'], parent_node=parent_node)
        
        return '', 201, {'Location': url_for('.item_by_id', item_id=node.id)}


@bp.route('/item/<int:item_id>', methods=('GET', 'PATCH', 'DELETE'))
def item_by_id(item_id):
    if item_id == Node.get_root_id():
        abort(404)

    node = Node.get_by_id(item_id)
    if node is None:
        abort(404)

    if request.method == 'GET':
        return jsonify(node.to_item)
    
    if request.method == 'DELETE':
        node.delete()
        return '', 204


@bp.route('/hierarchy', methods=('GET',))
def hierarchy():
    return jsonify(Node.get_by_id(Node.get_root_id()).get_subtree()['children'])


@bp.route('/subtree/<int:root_item_id>', methods=('GET',))
def subtree(root_item_id):
    node = Node.get_by_id(root_item_id)
    if node is None:
        abort(404)
        
    return jsonify(node.get_subtree())
