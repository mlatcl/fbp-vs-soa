from flask import (Blueprint, request, make_response, jsonify)
from .data import data_manager

bp = Blueprint('data_manager', __name__, url_prefix='/data-request')


# Get ride data to save API
@bp.route('/get_ride_data_to_save', methods=('GET', 'POST'))
def get_ride_data_to_save():
    req = request.get_json()
    data = data_manager.get_ride_data_to_save(req)
    res = make_response(jsonify(data), 200)
    return res


# Get wait times data to save API
@bp.route('/get_wait_times_data_to_save', methods=('GET', 'POST'))
def get_wait_times_data_to_save():
    req = request.get_json()
    data = data_manager.get_wait_times_data_to_save(req)
    res = make_response(jsonify(data), 200)
    return res


# Save data to a file API
@bp.route('/save_data_to_file', methods=('GET', 'POST'))
def save_data_to_file():
    req = request.get_json()
    res = data_manager.save_data_to_file(req)
    if res:
        res = make_response({}, 200)
    else:
        res = make_response({}, 500)
    return res

