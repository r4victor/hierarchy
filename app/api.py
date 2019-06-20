from flask import Blueprint

bp = Blueprint('api', __name__)

@bp.route('/item', methods=('POST', 'PUT'))
def item():
    return 'SO'

@bp.route('/item/<int:item_id>', methods=('GET', 'PATCH', 'DELETE'))
def item_(item_id):
    return 'SO'
