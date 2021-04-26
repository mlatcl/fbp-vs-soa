import requests

base_url='http://127.0.0.1:5000/'


# Client to add drivers data
def add_drivers_data(driver_statuses, driver_locations):
    if len(driver_statuses) > 0:
        drivers = {}
        for driver_status in driver_statuses:
            driver = {}
            driver['driver_id'] = driver_status.driver_id
            driver['update_time'] = str(driver_status.update_time)
            driver['state'] = driver_status.state.value
            drivers[(driver['driver_id'])] = driver
        for driver_location in driver_locations:
            driver = drivers[driver_location.driver_id]
            driver['location_time'] = str(driver_location.location_time)
            driver['lat'] = driver_location.location.lat
            driver['lon'] = driver_location.location.lon
            drivers[(driver['driver_id'])] = driver
        url = base_url + 'driver/add_all_drivers'
        response = requests.post(url, json=drivers)
        print(response.json())


# Client to add rides data
def add_rides_data(ride_requests):
    if len(ride_requests) > 0:
        rides = []
        for ride_request in ride_requests:
            ride = {}
            ride['ride_id'] = ride_request.ride_id
            ride['user_id'] = ride_request.user_id
            ride['request_time'] = str(ride_request.request_time)
            ride['from_lat'] = ride_request.from_location.lat
            ride['from_lon'] = ride_request.from_location.lon
            ride['to_lat'] = ride_request.to_location.lat
            ride['to_lon'] = ride_request.to_location.lon
            rides.append(ride)
        url = base_url + 'ride/add_all_rides'
        response = requests.post(url, json=rides)
        print(response.json())


class App():
    def __init__(self):
        self._build()

    def add_data(self, driver_statuses, driver_locations, ride_requests, ride_events, ride_infos):
        add_drivers_data(driver_statuses, driver_locations)
        add_rides_data(ride_requests)
        # TO DO: Information update when events start happening.
        # Methods above can be reused.

    def evaluate(self):
        print('Evaluating clients!')

    def get_outputs(self):
        print('Get outputs clients!')

    def _build(self):
        print('SOA app built!')


if __name__ == "__main__":
    app = App()
