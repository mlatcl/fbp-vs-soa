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

@bp.route('/filter', methods=['GET'])
def filter_movies():
    genre = request.args.get('genre', None)
    if genre is None or len(genre) == 0:
        return "Genre not provided", 400

    movie_ids = movie.filter_movies(genre)
    res = make_response(jsonify(movie_ids), 200)
    return res

@bp.route('/bonus', methods=['GET'])
def get_bonus_movie():
    movie_id = movie.get_random_movie()
    res = make_response(str(movie_id), 200)
    res.mimetype = "text/plain"
    return res