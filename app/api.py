from flask import Blueprint, request

from app.models import Node

bp = Blueprint('api', __name__)


@bp.route('/item', methods=('POST', 'PUT'))
def item():
    data = request.get_json()
    Node.create(name=data['name'], parent_id=data['parent_id'])
    return '!'


@bp.route('/item/<int:item_id>', methods=('GET', 'PATCH', 'DELETE'))
def item_(item_id):
    node = Node.get_by_id(item_id)
    if request.method == 'GET':
        return repr(node)
    
    if request.method == 'DELETE':
        node.delete()
        return ''


@bp.route('/subtree/<int:root_node_id>', methods=('GET',))
def subtree(root_node_id):
    root_node = Node.get_by_id(root_node_id)
    return str(root_node.get_subtree())
