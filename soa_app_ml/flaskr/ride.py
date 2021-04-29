from flask import (Blueprint, request, make_response, jsonify)
from .data import ride

bp = Blueprint('ride', __name__, url_prefix='/ride-request')


# Add a list of drivers API
@bp.route('/add_all_rides', methods=('GET', 'POST'))
def add_all_rides():
    res = {}
    req = request.get_json()
    rides = ride.insert_rides(req)
    res['msg'] = 'Rides affected = ' + str(rides)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of ride events API
@bp.route('/add_ride_events', methods=('GET', 'POST'))
def add_ride_events():
    res = {}
    req = request.get_json()
    rides = ride.update_rides_events(req)
    res['msg'] = 'Rides affected = ' + str(rides)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of ride infos API
@bp.route('/add_ride_infos', methods=('GET', 'POST'))
def add_ride_infos():
    res = {}
    req = request.get_json()
    rides = ride.update_rides_infos(req)
    res['msg'] = 'Rides affected = ' + str(rides)
    res = make_response(jsonify(res), 200)
    return res


# Get a list of ride infos API
@bp.route('/get_ride_infos', methods=('GET', 'POST'))
def get_ride_infos():
    req = request.get_json()
    res = ride.get_ride_infos()
    res = make_response(jsonify(res), 200)
    return res


# Get a list of ride wait times infos API
@bp.route('/get_ride_wait_times', methods=('GET', 'POST'))
def get_ride_wait_times():
    req = request.get_json()
    res = ride.get_ride_wait_times()
    res = make_response(jsonify(res), 200)
    return res


# Get all rides API
@bp.route('/get_all_rides', methods=('GET', 'POST'))
def get_all_rides():
    res = ride.get_all_rides()
    res = make_response(jsonify(res), 200)
    return res


# Get all rides API
@bp.route('/get_rides_by_state', methods=('GET', 'POST'))
def get_rides_by_state():
    req = request.get_json()
    res = ride.get_rides_by_state(req['state'])
    res = make_response(jsonify(res), 200)
    return res


# Update ride allocation
@bp.route('/update_ride_allocation', methods=('GET', 'POST'))
def update_ride_allocation():
    req = request.get_json()
    res = ride.update_ride_allocation(req)
    res = {'affected_rides': res}
    res = make_response(jsonify(res), 200)
    return res
