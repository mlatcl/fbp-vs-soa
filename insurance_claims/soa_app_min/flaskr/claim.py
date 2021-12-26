from flask import (Blueprint, request, make_response, jsonify)
from .data import claim
from datetime import datetime, timedelta

bp = Blueprint('claim', __name__, url_prefix='/claim-request')


# let's invent some kind of overhead that goes into processing the claim
CLAIM_VALUE_PROCESSING_OVERHEAD_RATE = 0.05

# threshold to decide if claim is high or low value
HIGH_VALUE_CLAIM_THRESHOLD = 60000

# claims below this value are considered simple
SIMPLE_CLAIM_VALUE_THRESHOLD = 5000

# in reality sometimes the claims will be paid in full, and sometimes partially or not at all
# to average this out let's just always pay out a certain partial amount
# we assume simple claims will be paid out more often
SIMPLE_CLAIMS_PAYOUT_RATE = 0.8
COMPLEX_CLAIMS_PAYOUT_RATE = 0.6


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
@bp.route('/calculate_claims_value', methods=('GET', 'POST'))
def calculate_claims_value():
    res = claim.get_claims_amount()
    for record in res:
        record['value'] = (1.0 + CLAIM_VALUE_PROCESSING_OVERHEAD_RATE) * record['value']
    res = make_response(jsonify(res), 200)
    return res


# Classify claims API
@bp.route('/classify_claims_value', methods=('GET', 'POST'))
def classify_claims_value():
    claims = request.get_json()
    high_value_claims = []
    low_value_claims = []
    for c in claims:
        if c['value'] >= HIGH_VALUE_CLAIM_THRESHOLD:
            high_value_claims.append(c)
        else:
            low_value_claims.append(c)
    res = {'high_value_claims': high_value_claims, 'low_value_claims': low_value_claims}

    res = make_response(jsonify(res), 200)
    return res


# Classify claims complexity API
@bp.route('/classify_claims_complexity', methods=('GET', 'POST'))
def classify_claims_complexity():
    req = request.get_json()
    low_value_claims = req['low_value_claims']
    high_value_claims = req['high_value_claims']
    simple_claims = []
    complex_claims = []
    for low_value_claim in low_value_claims:
        claim_classification_data = claim.get_claim_classification_data(low_value_claim['claim_id'])
        c = {'claim_id':claim_classification_data['claim_id'],
             'total_claim_amount': claim_classification_data['total_claim_amount']}
        if _is_claim_complex(claim_classification_data):
            complex_claims.append(c)
        else:
            simple_claims.append(c)

    for high_value_claim in high_value_claims:
        claim_classification_data = claim.get_claim_classification_data(high_value_claim['claim_id'])
        c = {'claim_id':claim_classification_data['claim_id'],
             'total_claim_amount': claim_classification_data['total_claim_amount']}
        complex_claims.append(c)

    res = {'simple_claims': simple_claims, 'complex_claims': complex_claims}
    res = make_response(jsonify(res), 200)
    return res


# just some almost random logic here
def _is_claim_complex(c):
    if c["total_claim_amount"] <= SIMPLE_CLAIM_VALUE_THRESHOLD:
        # small claims are never complex
        return False

    if c["auto_year"] < 2000:
        # old cars yield complex cases
        return True

    if c["witnesses"] == 0 and c["police_report_available"] != "YES":
        # no objective evidence of incident cause
        return True

    return False


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
    simple_claims = req['simple_claims']
    complex_claims = req['complex_claims']
    res = []

    for simple_claim in simple_claims:
        payout = SIMPLE_CLAIMS_PAYOUT_RATE * simple_claim["total_claim_amount"]
        r = {'claim_id': simple_claim['claim_id'], 'payout': payout}
        res.append(r)

    for complex_claim in complex_claims:
        payout = COMPLEX_CLAIMS_PAYOUT_RATE * complex_claim["total_claim_amount"]
        r = {'claim_id': complex_claim['claim_id'], 'payout': payout}
        res.append(r)

    for c in res:
        claim.mark_claim_processed(c["claim_id"])

    res = make_response(jsonify(res), 200)
    return res
