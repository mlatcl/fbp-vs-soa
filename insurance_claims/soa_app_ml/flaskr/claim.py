from flask import (Blueprint, request, make_response, jsonify)
from .data import claim
from datetime import datetime, timedelta

bp = Blueprint('claim', __name__, url_prefix='/claim-request')


# Add a list of claims API
@bp.route('/add_claims', methods=('GET', 'POST'))
def add_claims():
    res = {}
    req = request.get_json()
    affected = 0
    for c in req:
        affected = claim.create_claim(c)
    res['msg'] = 'Claims created = ' + str(affected)
    res = make_response(jsonify(res), 200)
    return res


# Classify claims API
@bp.route('/get_claims_info', methods=('GET', 'POST'))
def get_claims_info():
    req = request.get_json()
    res = claim.get_claims_info(req)
    res = make_response(jsonify(res), 200)
    return res


# Classify claims API
@bp.route('/calculate_claims_value', methods=('GET', 'POST'))
def calculate_claims_value():
    res = claim.calculate_claims_value()
    res = make_response(jsonify(res), 200)
    return res


# Classify claims API
@bp.route('/classify_claims_value', methods=('GET', 'POST'))
def classify_claims_value():
    req = request.get_json()
    res = claim.classify_claims_value(req)
    res = make_response(jsonify(res), 200)
    return res


# Classify claims complexity API
@bp.route('/classify_claims_complexity', methods=('GET', 'POST'))
def classify_claims_complexity():
    req = request.get_json()
    res = claim.classify_claims_complexity(req)
    res = make_response(jsonify(res), 200)
    return res


# Update claims API
@bp.route('/update_claims_complexity', methods=('GET', 'POST'))
def update_claims_complexity():
    req = request.get_json()
    res = claim.update_claims_complexity(req)
    res = make_response(jsonify(res), 200)
    return res


# Calculate claims payments API
@bp.route('/calculate_payments', methods=('GET', 'POST'))
def calculate_payments():
    req = request.get_json()
    res = claim.calculate_payments(req)
    res = make_response(jsonify(res), 200)
    return res


# Save claims API
@bp.route('/save_claims', methods=('GET', 'POST'))
def save_claims():
    req = request.get_json()
    res = claim.save_claims(req)
    res = make_response(jsonify(res), 200)
    return res

