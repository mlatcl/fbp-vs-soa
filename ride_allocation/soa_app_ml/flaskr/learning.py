from flask import (Blueprint, request, make_response, jsonify)
import pickle
import os.path


bp = Blueprint('learning', __name__, url_prefix='/learning-request')


# Get estimated times API
@bp.route('/get_estimated_times', methods=('GET', 'POST'))
def get_estimated_times():
    req = request.get_json()
    model = None
    if os.path.isfile("soa_model.obj"):
        with open("soa_model.obj", "rb") as f:
            model = pickle.load(f)
    else:
        model = None
    estimates = []
    for ride in req:
        if ride['state'] == 'DRIVER_ASSIGNED':
            X = [[ride['driver_info']['location']['lat'], ride['driver_info']['location']['lon'],
                ride['last_location']['lat'], ride['last_location']['lon']]]
            model_output = 0.0
            if model is not None:
                model_output = model.predict(X)[0]
            else:
                model_output = 0.0
            estimate = {'ride_id': ride['ride_id'], 'wait_time': model_output}
            estimates.append(estimate)
    res = make_response(jsonify(estimates), 200)
    return res
