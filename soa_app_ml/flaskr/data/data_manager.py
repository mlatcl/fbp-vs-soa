# Drivers information
import pandas as pd
import os.path


# Get ride data to save
def get_ride_data_to_save(ride_infos):
    rides = []
    for ride_info in ride_infos:
        if ride_info['state'] == 'DRIVER_ASSIGNED':
            ride = {'ride_id': ride_info['ride_id'], 'driver_id': ride_info['driver_id'],
                    'user_lat': ride_info['last_location']['lat'], 'user_lon': ride_info['last_location']['lon']}
            rides.append(ride)
    return rides


# Get ride data to save
def get_wait_times_data_to_save(ride_wait_times):
    wait_times = []
    for ride_wait_time in ride_wait_times:
        wait_time = {'ride_id': ride_wait_time['ride_id'], 'wait_duration': ride_wait_time['wait_duration']}
        wait_times.append(wait_time)
    return wait_times


# Save data to a file
def save_data_to_file(content):
    """
            Writes data from given pandas DataFrame to file
            Creates new file (with header) if it doesn't exist
            otherwise appends data to existing file

            Does not do anything if the dataset is empty
            """

    dataset_records = content['info']
    file_name = content['file_name']
    df = pd.DataFrame(dataset_records)

    if df.empty:
        return True

    if os.path.isfile(file_name):
        df.to_csv(file_name, mode="a", index=False, header=False)
        return True
    else:
        df.to_csv(file_name, mode="w", index=False, header=True)
        return True
    return False
