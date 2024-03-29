from flask import (Blueprint, request, make_response, jsonify)
from .data import post

bp = Blueprint('post', __name__, url_prefix='/post-request')


# Create a new post
@bp.route('/create_posts', methods=('GET', 'POST'))
def create_posts():
    res = {}
    req = request.get_json()
    for r in req:
        affected = post.create_post(r)
    res['msg'] = 'New posts created = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# Get timeline for a given author
@bp.route('/get_timelines', methods=('GET', 'POST'))
def get_timelines():
    res = post.get_timelines()
    res = make_response(jsonify(res), 200)
    return res
