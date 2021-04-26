from flask import (Blueprint, request, make_response, jsonify)
from .data import driver


bp = Blueprint('driver', __name__, url_prefix='/driver')


@bp.route('/new_driver', methods=('GET', 'POST'))
def new_driver():
    req = None
    last_latitude = None
    last_longitude = None
    last_state = None

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
        print(str(req))

    if 'last_latitude' in req:
        last_latitude = req['last_latitude']
    else:
        res['error'] = 'Driver last latitude is required.'
        res = make_response(jsonify(res), 400)
        return res
    if 'last_longitude' in req:
        last_longitude = req['last_longitude']
    else:
        res['error'] = 'Driver last longitude is required.'
        res = make_response(jsonify(res), 400)
        return res
    if 'last_state' in req:
        last_state = req['last_state']
    else:
        res['error'] = 'Driver last status is required.'
        res = make_response(jsonify(res), 400)
        return res
    driver_id = driver.insert_driver(req)
    print('New driver registered with ID = ' + str(driver_id))

    res['msg'] = 'New driver registered with ID = ' + str(driver_id)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of drivers API
@bp.route('/add_all_drivers', methods=('GET', 'POST'))
def add_all_drivers():
    print('Request before print = ' + str(request))
    res = {}
    req = request.get_json()
    print('Request print = ' + str(req))
    drivers = driver.insert_drivers(req)
    print('Drivers affected = ' + str(drivers))
    res['msg'] = 'Drivers affected = ' + str(drivers)
    res = make_response(jsonify(res), 200)
    return res

# Update driver API
@bp.route('/update_driver', methods=('GET', 'POST'))
def update_driver():
    req = None
    driver_id = None
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

    if 'driver_id' in req:
        driver_id = req['driver_id']
        del req['driver_id']
    else:
        res['error'] = 'Ride ID is required.'
        res = make_response(jsonify(res), 400)
        return res

    driver_id = driver.update_driver(driver_id, req)
    print('Updated driver registered with ID = ' + str(driver_id))
    res['msg'] = 'Updated driver registered with ID = ' + str(driver_id)
    res = make_response(jsonify(res), 200)
    return res


# Get all drivers API
@bp.route('/get_all_drivers', methods=('GET', 'POST'))
def get_all_drivers():
    res = driver.get_all_drivers()
    res = make_response(jsonify(res), 200)
    return res


# Get available drivers API
@bp.route('/get_available_drivers', methods=('GET', 'POST'))
def get_available_drivers():
    res = driver.get_available_drivers()
    print("RES =>" + str(res))
    res = make_response(jsonify(res), 200)
    return res


# Get driver by ID API
@bp.route('/get_driver', methods=('GET', 'POST'))
def get_driver():
    req = None
    driver_id = None
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

    if 'driver_id' in req:
        driver_id = req['driver_id']
    else:
        res['error'] = 'Driver ID is required.'
        res = make_response(jsonify(res), 400)
        return res
    d = driver.get_driver(driver_id)
    if d is None:
        res['error'] = 'Driver ID ' + str(driver_id) + '  not found.'
        res = make_response(jsonify(res), 400)
        return res
    res = make_response(jsonify(d), 200)
    return res

