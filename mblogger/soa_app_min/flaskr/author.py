from flask import (Blueprint, request, make_response, jsonify)
from .data import author

bp = Blueprint('author', __name__, url_prefix='/author-request')


# Registers a new author
@bp.route('/registers', methods=('GET', 'POST'))
def registers_author():
    res = {}
    req = request.get_json()
    affected = author.registers_author(req)
    res['msg'] = 'Registered author = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# Follows an author
@bp.route('/follows', methods=('GET', 'POST'))
def follows_author():
    res = {}
    req = request.get_json()
    affected = author.follows_author(req)
    res['msg'] = 'Following author = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# List author follows
@bp.route('/list_follows', methods=('GET', 'POST'))
def list_follows():
    res = {}
    req = request.get_json()
    res = author.get_list_follows(req)
    res = make_response(jsonify(res), 200)
    return res


# List author followers
@bp.route('/list_followers', methods=('GET', 'POST'))
def list_followers():
    res = {}
    req = request.get_json()
    res = author.get_list_followers(req)
    res = make_response(jsonify(res), 200)
    return res
