from flask import (Blueprint, request, make_response, jsonify)
from .data import driver
import json


bp = Blueprint('driver', __name__, url_prefix='/driver-request')


# Add a list of drivers statuses API
@bp.route('/add_all_drivers_statuses', methods=('GET', 'POST'))
def add_all_drivers_statuses():
    res = {}
    req = request.get_json()
    print('Request print = ' + str(req))
    drivers = driver.insert_drivers(req)
    print('Drivers affected = ' + str(drivers))
    res['msg'] = 'Drivers affected = ' + str(drivers)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of drivers locations API
@bp.route('/add_all_drivers_locations', methods=('GET', 'POST'))
def add_all_drivers_locations():
    print('Request before print = ' + str(request))
    res = {}
    req = request.get_json()
    print('Request print = ' + str(req))
    drivers = driver.insert_drivers(req)
    print('Drivers affected = ' + str(drivers))
    res['msg'] = 'Drivers affected = ' + str(drivers)
    res = make_response(jsonify(res), 200)
    return res


# Allocate drivers to rides API
@bp.route('/allocate_drivers', methods=('GET', 'POST'))
def allocate_drivers():
    res = {}
    allocation = driver.allocate_drivers()
    res = make_response(jsonify(allocation), 200)
    return res


# Get all drivers API
@bp.route('/get_all_drivers', methods=('GET', 'POST'))
def get_all_drivers():
    res = driver.get_all_drivers()
    res = make_response(jsonify(res), 200)
    return res