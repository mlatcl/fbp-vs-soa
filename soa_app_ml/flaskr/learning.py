from flask import (Blueprint, request, make_response, jsonify)
import pickle
import pandas as pd
from sklearn.linear_model import LinearRegression
import os.path

bp = Blueprint('learning', __name__, url_prefix='/learning-request')


# Train model API
@bp.route('/train_model', methods=('GET', 'POST'))
def train_model():
    allocation_df = pd.read_csv("allocate_ride_soa_app.csv", header=0)
    allocation_df = allocation_df.drop_duplicates(subset=["ride_id"])
    allocation_df.set_index('ride_id', inplace=True)

    wait_time_df = pd.read_csv("wait_time_soa_app.csv", header=0)
    wait_time_df = wait_time_df.drop_duplicates(subset=["ride_id"])
    wait_time_df.set_index("ride_id", inplace=True)

    dataset_df = allocation_df.join(wait_time_df, how="left")
    dataset_df = dataset_df.dropna()

    X = dataset_df[["driver_lat", "driver_lon", "user_lat", "user_lon"]]
    y = pd.to_timedelta(dataset_df["wait_duration"]).dt.seconds

    model = LinearRegression().fit(X, y)
    print("MAE: ", (model.predict(X) - y).abs().mean())
    print("MSE: ", (model.predict(X) - y).pow(2).mean())

    with open("soa_model.obj", "wb") as f:
        pickle.dump(model, f)
    res = make_response(jsonify({}), 200)
    return res


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
            print(str(estimate))
            estimates.append(estimate)
    print(str(estimates))
    res = make_response(jsonify(estimates), 200)
    return res
