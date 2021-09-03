from flask import (Blueprint, request, make_response, jsonify)
from .predict import learning

bp = Blueprint('learning', __name__, url_prefix='/predict-request')


# Predict claims complexity API
@bp.route('/predict_claims_complexity', methods=('GET', 'POST'))
def predict_claims_complexity():
    req = request.get_json()
    res = learning.predict_claims_complexity(req)
    res = make_response(jsonify(res), 200)
    return res
