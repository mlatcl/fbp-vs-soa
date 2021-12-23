from flask import (Blueprint, request, make_response, jsonify)
from .data import movie

bp = Blueprint('movie', __name__, url_prefix='/movie')

@bp.route('/add', methods=['POST'])
def add_movie():
    res = {}
    affected = 0
    req = request.get_json()
    affected = movie.create_movie(req)
    res['msg'] = 'Movies added = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res
