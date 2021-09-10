from flask import (Blueprint, request, make_response, jsonify)
from .data import author

bp = Blueprint('author', __name__, url_prefix='/author-request')


# Follows an author
@bp.route('/follows', methods=('GET', 'POST'))
def follows_author():
    res = {}
    req = request.get_json()
    for r in req:
        if r['follow']:
            r['follow'] = 1
        else:
            r['follow'] = 0
        affected = author.follows_author(r)
    res['msg'] = 'New follows added = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# List author followers
@bp.route('/list_followers', methods=('GET', 'POST'))
def list_followers():
    res = author.get_list_followers()
    res = make_response(jsonify(res), 200)
    return res


# List author followings
@bp.route('/list_followings', methods=('GET', 'POST'))
def list_followings():
    res = author.get_list_followings()
    res = make_response(jsonify(res), 200)
    return res
