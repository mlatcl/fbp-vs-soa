import requests
import json


base_url='http://127.0.0.1:5000/'


# Client to add drivers status data
def add_driver_statuses_data(driver_statuses):
    if len(driver_statuses) > 0:
        d_statuses = []
        for driver_status in driver_statuses:
            d_status = driver_status.to_dict()
            d_status['update_time'] = str(driver_status.update_time)
            d_status['state'] = driver_status.state.value
            d_statuses.append(d_status)
        url = base_url + 'driver-request/add_all_drivers_statuses'
        response = requests.post(url, json=d_statuses)
        print(response.json())


# Client to add drivers location data
def add_driver_locations_data(driver_locations):
    if len(driver_locations) > 0:
        d_locations = []
        for driver_location in driver_locations:
            d_location = driver_location.to_dict()
            d_location['location_time'] = str(driver_location.location_time)
            d_locations.append(d_location)
        url = base_url + 'driver-request/add_all_drivers_locations'
        response = requests.post(url, json=d_locations)
        print(response.json())


# Client to add rides data
def add_rides_data(ride_requests):
    if len(ride_requests) > 0:
        rides = []
        for ride_request in ride_requests:
            ride = ride_request.to_dict()
            ride['request_time'] = str(ride_request.request_time)
            rides.append(ride)
        url = base_url + 'ride-request/add_all_rides'
        response = requests.post(url, json=rides)
        print(response.json())


class App():

    def add_data(self, driver_statuses, driver_locations, ride_requests, ride_events, ride_infos):
        add_driver_statuses_data(driver_statuses)
        add_driver_locations_data(driver_locations)
        add_rides_data(ride_requests)
        # TO DO: Information update when events start happening.
        # Methods above can be reused.

    def evaluate(self):
        print('Evaluating clients!')

    def get_outputs(self):
        print('Get outputs clients!')


if __name__ == "__main__":
    app = App()
