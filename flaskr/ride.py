from flask import (Blueprint, request, make_response, jsonify)
from .data import ride


bp = Blueprint('ride', __name__, url_prefix='/ride-request')


# Add a list of drivers API
@bp.route('/add_all_rides', methods=('GET', 'POST'))
def add_all_rides():
    res = {}
    req = request.get_json()
    print('Request print = ' + str(req))
    rides = ride.insert_rides(req)
    print('Rides affected = ' + str(rides))
    res['msg'] = 'Rides affected = ' + str(rides)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of ride events API
@bp.route('/add_ride_events', methods=('GET', 'POST'))
def add_ride_events():
    res = {}
    req = request.get_json()
    print('Request print = ' + str(req))
    rides = ride.update_rides_events(req)
    print('Rides affected = ' + str(rides))
    res['msg'] = 'Rides affected = ' + str(rides)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of ride infos API
@bp.route('/add_ride_infos', methods=('GET', 'POST'))
def add_ride_infos():
    res = {}
    req = request.get_json()
    print('Request print = ' + str(req))
    rides = ride.update_rides_infos(req)
    print('Rides affected = ' + str(rides))
    res['msg'] = 'Rides affected = ' + str(rides)
    res = make_response(jsonify(res), 200)
    return res


# Get all rides API
@bp.route('/get_all_rides', methods=('GET', 'POST'))
def get_all_rides():
    res = ride.get_all_rides()
    res = make_response(jsonify(res), 200)
    return res