from flask import (Blueprint, request, make_response, jsonify)
import pandas as pd
import os.path

bp = Blueprint('data_manager', __name__, url_prefix='/data-request')


# Get ride data to save API
@bp.route('/get_ride_data_to_save', methods=('GET', 'POST'))
def get_ride_data_to_save():
    req = request.get_json()
    rides = []
    for ride_info in req:
        if ride_info['state'] == 'DRIVER_ASSIGNED':
            ride = {'ride_id': ride_info['ride_id'], 'driver_id': ride_info['driver_id'],
                    'user_lat': ride_info['last_location']['lat'], 'user_lon': ride_info['last_location']['lon']}
            rides.append(ride)
    res = make_response(jsonify(rides), 200)
    return res


# Get wait times data to save API
@bp.route('/get_wait_times_data_to_save', methods=('GET', 'POST'))
def get_wait_times_data_to_save():
    req = request.get_json()
    wait_times = []
    for ride_wait_time in req:
        wait_time = {'ride_id': ride_wait_time['ride_id'], 'wait_duration': ride_wait_time['wait_duration']}
        wait_times.append(wait_time)
    res = make_response(jsonify(wait_times), 200)
    return res


# Save data to a file API
@bp.route('/save_data_to_file', methods=('GET', 'POST'))
def save_data_to_file():
    req = request.get_json()
    """
                Writes data from given pandas DataFrame to file
                Creates new file (with header) if it doesn't exist
                otherwise appends data to existing file

                Does not do anything if the dataset is empty
                """

    dataset_records = req['info']
    file_name = req['file_name']
    df = pd.DataFrame(dataset_records)
    res = False
    if df.empty:
        res = True

    if os.path.isfile(file_name):
        df.to_csv(file_name, mode="a", index=False, header=False)
        res = True
    else:
        df.to_csv(file_name, mode="w", index=False, header=True)
        res = True
    if res:
        res = make_response({}, 200)
    else:
        res = make_response({}, 500)
    return res

