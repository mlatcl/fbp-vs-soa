from flask import (Blueprint, request, make_response, jsonify)
from .data import ride


bp = Blueprint('ride', __name__, url_prefix='/ride-request')


# New ride API
@bp.route('/new_ride', methods=('GET', 'POST'))
def new_ride():
    req = None
    user_id = None
    from_latitude = None
    from_longitude = None
    to_latitude = None
    to_longitude = None
    res = {}
    if request.method == 'GET':
        if request.args:
            req = request.args
        else:
            res['error'] = 'Request without arguments.'
            res = make_response(jsonify(res), 400)
            return res
    if request.method == 'POST':
        req = request.get_json()

    print('New request: ' + str(req))

    if 'user_id' in req:
        user_id = req['user_id']
    else:
        res['error'] = 'User ID is required.'
        res = make_response(jsonify(res), 400)
        return res
    if 'from_latitude' in req:
        from_latitude = req['from_latitude']
    else:
        res['error'] = 'Initial latitude is required.'
        res = make_response(jsonify(res), 400)
        return res
    if 'from_longitude' in req:
        from_longitude = req['from_longitude']
    else:
        res['error'] = 'Initial longitude is required.'
        res = make_response(jsonify(res), 400)
        return res
    if 'to_latitude' in req:
        to_latitude = req['to_latitude']
    else:
        res['error'] = 'Final latitude is required.'
        res = make_response(jsonify(res), 400)
        return res
    if 'to_longitude' in req:
        to_longitude = req['to_longitude']
    else:
        res['error'] = 'Final longitude is required.'
        res = make_response(jsonify(res), 400)
        return res

    ride_id = ride.insert_ride(user_id, from_latitude, from_longitude, to_latitude, to_longitude, 'RIDE', 'DATA')
    print('New ride registered with ID = ' + str(ride_id))
    res['msg'] = 'New ride registered with ID = ' + str(ride_id)
    res = make_response(jsonify(res), 200)
    return res


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


# Update ride API
@bp.route('/update_ride', methods=('GET', 'POST'))
def update_ride():
    req = None
    ride_id = None
    state = None
    res = {}
    if request.method == 'GET':
        if request.args:
            req = request.args
        else:
            res['error'] = 'Request without arguments.'
            res = make_response(jsonify(res), 400)
            return res
    if request.method == 'POST':
        req = request.get_json()

    print('New request: ' + str(req))

    if 'ride_id' in req:
        ride_id = req['ride_id']
    else:
        res['error'] = 'Ride ID is required.'
        res = make_response(jsonify(res), 400)
        return res
    if 'state' in req:
        state = req['state']
    else:
        res['error'] = 'Ride status is required.'
        res = make_response(jsonify(res), 400)
        return res
    ride_id = ride.update_ride(ride_id, state)
    if ride_id is None:
        res['error'] = 'Ride ID ' + str(ride_id) + '  not found.'
        res = make_response(jsonify(res), 400)
        return res
    print('Updated ride registered with ID = ' + str(ride_id))
    res['msg'] = 'Updated ride registered with ID = ' + str(ride_id)
    res = make_response(jsonify(res), 200)
    return res


# Get all rides API
@bp.route('/get_all_rides', methods=('GET', 'POST'))
def get_all_rides():
    res = ride.get_all_rides()
    res = make_response(jsonify(res), 200)
    return res


# Get ride by ID API
@bp.route('/get_ride', methods=('GET', 'POST'))
def get_ride():
    req = None

    ride_id = None
    res = {}
    if request.method == 'GET':
        if request.args:
            req = request.args
        else:
            res['error'] = 'Request without arguments.'
            res = make_response(jsonify(res), 400)
            return res
    if request.method == 'POST':
        req = request.get_json()

    print('New request: ' + str(req))

    if 'ride_id' in req:
        ride_id = req['ride_id']
    else:
        res['error'] = 'Ride ID is required.'
        res = make_response(jsonify(res), 400)
        return res
    res = ride.get_ride(ride_id)
    if res is None:
        res['error'] = 'Ride ID ' + str(ride_id) + '  not found.'
        res = make_response(jsonify(res), 400)
        return res
    res = make_response(jsonify(res), 200)
    return res

