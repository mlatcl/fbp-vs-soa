from distutils.util import strtobool
from random import shuffle

from flask import (Blueprint, request, make_response, jsonify)
import requests
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


@bp.route('/request/all', methods=['GET'])
def get_playlist_requests():
    is_processed_param = request.args.get("is_processed", None)
    is_processed = bool(strtobool(is_processed_param))
    requests = playlist.get_playlist_requests(is_processed)
    res = make_response(jsonify(requests), 200)
    return res


@bp.route('/build', methods=['GET'])
def build_playlist():
    req = request.get_json()
    movie_ids = req["movie_ids"]
    bonus_movie_id = req["bonus_movie_id"]
    count = int(req["count"])

    shuffle(movie_ids)
    playlist_movies = [bonus_movie_id] + movie_ids
    playlist_movies = playlist_movies[:count]

    res = make_response(jsonify(playlist_movies), 200)
    return res


@bp.route('/save', methods=['POST'])
def save_playlist():
    req = request.get_json()
    affected = playlist.save_playlist(req)

    message = 'Rows added = ' + str(affected)
    res = make_response(message, 200)
    res.mimetype = "text/plain"
    return res


@bp.route('/load', methods=['GET'])
def load_playlist():
    request_id_param = request.args["request_id"]
    request_id = int(request_id_param)

    movies = playlist.load_playlist_movies(request_id)
    res = {
        "request_id": request_id,
        'movies': movies
    }
    res = make_response(jsonify(res), 200)
    return res
