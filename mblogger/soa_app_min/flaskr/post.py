from flask import (Blueprint, request, make_response, jsonify)
from .data import post

bp = Blueprint('post', __name__, url_prefix='/post-request')


# Create a new post
@bp.route('/create_post', methods=('GET', 'POST'))
def create_post():
    res = {}
    req = request.get_json()
    affected = post.create_post(req)
    res['msg'] = 'Post created = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# Get timeline for a given author
@bp.route('/get_timeline', methods=('GET', 'POST'))
def get_timeline():
    res = {}
    req = request.get_json()
    res = post.get_timeline(req)
    res = make_response(jsonify(res), 200)
    return res
