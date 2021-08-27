from flask import (Blueprint, request, make_response, jsonify)
from .data import post
from .data import words

bp = Blueprint('post', __name__, url_prefix='/post-request')


# Create a new post
@bp.route('/create_posts', methods=('GET', 'POST'))
def create_posts():
    res = {}
    req = request.get_json()
    for r in req:
        affected = post.create_post(r)
        words.update_bigrams(r)
        words.update_personal_directory(r)

    res['msg'] = 'New posts created = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# Get timeline for a given author
@bp.route('/get_timelines', methods=('GET', 'POST'))
def get_timelines():
    res = post.get_timelines()
    res = make_response(jsonify(res), 200)
    return res


# Get generated posts
@bp.route('/get_generated_posts', methods=('GET', 'POST'))
def get_generated_posts():
    res = post.get_generated_posts()
    res = make_response(jsonify(res), 200)
    return res


# Create generated posts
@bp.route('/generate_post', methods=('GET', 'POST'))
def generate_post():
    res = {}
    req = request.get_json()
    affected = post.generate_post(req)
    res['msg'] = 'New posts created = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res