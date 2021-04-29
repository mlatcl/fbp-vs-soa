from flask import (Blueprint, request, make_response, jsonify)
from .data import driver

bp = Blueprint('driver', __name__, url_prefix='/driver-request')


# Add a list of drivers statuses API
@bp.route('/add_all_drivers_statuses', methods=('GET', 'POST'))
def add_all_drivers_statuses():
    res = {}
    req = request.get_json()
    drivers = driver.insert_drivers(req)
    res['msg'] = 'Drivers affected = ' + str(drivers)
    res = make_response(jsonify(res), 200)
    return res


# Add a list of drivers locations API
@bp.route('/add_all_drivers_locations', methods=('GET', 'POST'))
def add_all_drivers_locations():
    res = {}
    req = request.get_json()
    drivers = driver.insert_drivers(req)
    res['msg'] = 'Drivers affected = ' + str(drivers)
    res = make_response(jsonify(res), 200)
    return res


# Allocate driver to ride API
@bp.route('/allocate_driver', methods=('GET', 'POST'))
def allocate_driver():
    req = request.get_json()
    res = driver.allocate_driver()
    res = make_response(jsonify(res), 200)
    return res


# Release driver
@bp.route('/release_driver', methods=('GET', 'POST'))
def release_driver():
    req = request.get_json()
    res = driver.release_driver(req["driver_id"])
    res = make_response(jsonify(res), 200)
    return res


# Get all drivers API
@bp.route('/get_all_drivers', methods=('GET', 'POST'))
def get_all_drivers():
    res = driver.get_all_drivers()
    res = make_response(jsonify(res), 200)
    return res