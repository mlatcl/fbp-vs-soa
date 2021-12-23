from flask import (Blueprint, request, make_response, jsonify)
from .data import playlist

bp = Blueprint('playlist', __name__, url_prefix='/playlist')

@bp.route('/request/add', methods=['POST'])
def add_playlist_request():
    res = {}
    affected = 0
    req = request.get_json()
    affected = playlist.create_playlist_request(req)
    res['msg'] = 'Requests added = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res
