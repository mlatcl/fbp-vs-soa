from flask import (Blueprint, request, make_response, jsonify)
from .data import ride
from datetime import datetime, timedelta

bp = Blueprint('ride', __name__, url_prefix='/ride-request')


# Add a list of drivers API
@bp.route('/add_all_rides', methods=('GET', 'POST'))
def add_all_rides():
    res = {}
    affected = 0
    req = request.get_json()
    for r in req:
        affected = ride.insert_ride(r)
    res['msg'] = 'Rides affected = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of ride events API
@bp.route('/add_ride_events', methods=('GET', 'POST'))
def add_ride_events():
    res = {}
    req = request.get_json()
    affected = 0
    for ride_event in req:
        ride_id = ride_event['ride_id']
        info = {'update_time': datetime.strptime(ride_event['event_time'], '%Y-%m-%d %H:%M:%S.%f'),
                'state': ride_event['ride_status'], 'event_type': ride_event['event_type'],
                'last_lat': ride_event['event_data']['location']['lat'],
                'last_lon': ride_event['event_data']['location']['lon']}
        upd = ride.update_ride(ride_id, info)
        if upd is not None:
            affected = affected + 1
    res['msg'] = 'Rides affected = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of ride infos API
@bp.route('/add_ride_infos', methods=('GET', 'POST'))
def add_ride_infos():
    res = {}
    req = request.get_json()
    affected = 0
    for ride_info in req:
        ride_id = ride_info['ride_id']
        info = {'user_id': ride_info['user_id'], 'driver_id': ride_info['driver_id'],
                'update_time': ride_info['update_time'], 'last_lat': ride_info['last_location']['lat'],
                'last_lon': ride_info['last_location']['lon']}
        upd = ride.update_ride(ride_id, info)
        if upd is not None:
            affected = affected + 1
    res['msg'] = 'Rides affected = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# Get a list of ride infos API
@bp.route('/get_ride_infos', methods=('GET', 'POST'))
def get_ride_infos():
    req = request.get_json()
    ride_infos = []
    assigned = ride.get_rides_by_state('DRIVER_ASSIGNED')
    enroute = ride.get_rides_by_state('ENROUTE')
    for r in assigned:
        ride_info = {'ride_id': r['ride_id'], 'user_id': r['user_id'], 'driver_id': r['driver_id'],
                     'state': r['state'], 'update_time': r['update_time'],
                     'last_location': r['last_location']}
        ride_infos.append(ride_info)
    for r in enroute:
        ride_info = {'ride_id': r['ride_id'], 'user_id': r['user_id'], 'driver_id': r['driver_id'],
                     'state': r['state'], 'update_time': r['update_time'],
                     'last_location': r['last_location']}
        ride_infos.append(ride_info)
    res = make_response(jsonify(ride_infos), 200)
    return res


# Get a list of ride wait times infos API
@bp.route('/get_ride_wait_times', methods=('GET', 'POST'))
def get_ride_wait_times():
    req = request.get_json()
    rides = ride.get_ride_wait_times()
    ride_wait_times = []
    for r in rides:
        wait_duration = r['allocation_time'] - r['request_time']
        wait_duration = wait_duration / timedelta(milliseconds=1)
        last_location = {'lat': r['last_lat'], 'lon': r['last_lon']}
        ride_wait_time = {'ride_id': r['ride_id'],
                          'request_time': r['request_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
                          'wait_duration': wait_duration, 'location': last_location}
        ride_wait_times.append(ride_wait_time)
        info = {'evaluated': 'done'}
        ride.update_ride(r['ride_id'], info)
    res = make_response(jsonify(ride_wait_times), 200)
    return res


# Get all rides API
@bp.route('/get_all_rides', methods=('GET', 'POST'))
def get_all_rides():
    res = ride.get_all_rides()
    res = make_response(jsonify(res), 200)
    return res


# Get all rides by state API
@bp.route('/get_rides_by_state', methods=('GET', 'POST'))
def get_rides_by_state():
    req = request.get_json()
    res = ride.get_rides_by_state(req['state'])
    res = make_response(jsonify(res), 200)
    return res


# Update ride allocation
@bp.route('/update_ride_allocation', methods=('GET', 'POST'))
def update_ride_allocation():
    ride_allocation = request.get_json()
    affected = 0
    ride_id = ride_allocation['ride_id']
    info = {'driver_id': ride_allocation['driver_id'], 'allocation_time': datetime.now(), 'update_time': datetime.now(),
            'state': ride_allocation['state']}
    res = ride.update_ride(ride_id, info)
    if res is not None:
        affected = affected + 1
    res = {'affected_rides': affected}
    res = make_response(jsonify(res), 200)
    return res
