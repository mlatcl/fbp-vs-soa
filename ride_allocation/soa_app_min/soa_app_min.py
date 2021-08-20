import requests
from datetime import datetime, timedelta
import json

from ..record_types import RideStatus, DriverStatus, DriverState, Location, RideInformation, RideWaitInfo

base_url = 'http://127.0.0.1:5000/'


class App():

    def add_data(self, driver_statuses, driver_locations, ride_requests, ride_events, ride_infos):
        self._add_driver_statuses_data(driver_statuses)
        self._add_driver_locations_data(driver_locations)
        self._add_ride_data(ride_requests)
        self._add_ride_events(ride_events)
        self._add_ride_infos(ride_infos)

    # Client to add drivers status data
    def _add_driver_statuses_data(self, driver_statuses):
        if len(driver_statuses) > 0:
            d_statuses = []
            for driver_status in driver_statuses:
                d_status = driver_status.to_dict()
                d_status['update_time'] = str(driver_status.update_time)
                d_status['state'] = driver_status.state.value
                d_statuses.append(d_status)
            url = base_url + 'driver-request/add_all_drivers_statuses'
            response = requests.post(url, json=d_statuses)
            # print(response.json())

    # Client to add drivers location data
    def _add_driver_locations_data(self, driver_locations):
        if len(driver_locations) > 0:
            d_locations = []
            for driver_location in driver_locations:
                d_location = driver_location.to_dict()
                d_location['location_time'] = str(driver_location.location_time)
                d_locations.append(d_location)
            url = base_url + 'driver-request/add_all_drivers_locations'
            response = requests.post(url, json=d_locations)
            # print(response.json())

    # Client to add rides data
    def _add_ride_data(self, ride_requests):
        if len(ride_requests) > 0:
            rides = []
            for ride_request in ride_requests:
                ride = ride_request.to_dict()
                ride['request_time'] = str(ride_request.request_time)
                ride['state'] = RideStatus.UNASSIGNED.value
                rides.append(ride)
            url = base_url + 'ride-request/add_all_rides'
            response = requests.post(url, json=rides)
            # print(response.json())

    # Client to add rides events
    def _add_ride_events(self, ride_events):
        if len(ride_events) > 0:
            rides = []
            for ride_event in ride_events:
                ride = ride_event.to_dict()
                ride['event_time'] = str(ride_event.event_time)
                ride['event_type'] = ride_event.event_type.value
                if ride['event_type'] == 'START':
                    ride['ride_status'] = RideStatus.ENROUTE.value
                if ride['event_type'] == 'COMPLETE':
                    ride['ride_status'] = RideStatus.COMPLETED.value
                if ride['event_type'] == 'CANCEL':
                    ride['ride_status'] = RideStatus.CANCELLED.value
                rides.append(ride)
            url = base_url + 'ride-request/add_ride_events'
            response = requests.post(url, json=rides)
            # print(response.json())

    # Client to add rides infos
    def _add_ride_infos(self, ride_infos):
        if len(ride_infos) > 0:
            rides = []
            for ride_info in ride_infos:
                ride = ride_info.to_dict()
                ride['update_time'] = str(ride_info.update_time)
                ride['ride_status'] = ride_info.ride_status.value
                ride['last_location'] = ride_info.last_location.to_dict()
                rides.append(ride)
            url = base_url + 'ride-request/add_ride_infos'
            response = requests.post(url, json=rides)
            # print(response.json())

    def evaluate(self):
        driver_allocations = self._allocate_drivers()
        ride_infos = self._get_ride_infos()
        ride_wait_times = self._get_ride_wait_times()
        return self.get_outputs(driver_allocations, ride_infos, ride_wait_times)

    # Allocate drivers
    def _allocate_drivers(self):
        driver_allocations = []
        rides = self._get_rides_by_state(RideStatus.UNASSIGNED.value)
        for ride in rides:
            driver_status = self._allocate_driver(ride['ride_id'])
            if driver_status is not None:
                response = self._update_ride_allocation(ride['ride_id'], driver_status['driver_id'],
                                                        RideStatus.DRIVER_ASSIGNED.value)
                if response.status_code == 200:
                    driver_allocations.append(driver_status)
                else:
                    self._release_driver(driver_status['ride_id'])
        return driver_allocations

    # Client to get rides by state
    def _get_rides_by_state(self, state):
        url = base_url + 'ride-request/get_rides_by_state'
        state = {'state': state}
        response = requests.post(url, json=state)
        rides = response.json()
        return rides

    # Client to allocate a driver
    def _allocate_driver(self, ride_id):
        url = base_url + 'driver-request/allocate_driver'
        info = {'ride_id': ride_id}
        response = requests.post(url, json=info)
        driver_status = response.json()
        return driver_status

    # Client to update ride allocation
    def _update_ride_allocation(self, ride_id, driver_id, state):
        url = base_url + 'ride-request/update_ride_allocation'
        info = {'ride_id': ride_id, 'driver_id': driver_id, 'state': state}
        return requests.post(url, json=info)

    # Client to release a driver
    def _release_driver(self, driver_id):
        url = base_url + 'driver-request/release_driver'
        info = {'driver_id': driver_id}
        requests.post(url, json=info)

    # Client to get ride infos
    def _get_ride_infos(self):
        url = base_url + 'ride-request/get_ride_infos'
        response = requests.post(url, json={})
        # print(response.json())
        return response.json()

    # Client to get wait times
    def _get_ride_wait_times(self):
        url = base_url + 'ride-request/get_ride_wait_times'
        response = requests.post(url, json={})
        # print(response.json())
        return response.json()

    # Parsing data for main programm
    def get_outputs(self, das, ris, rwts):
        driver_allocations = []
        for da in das:
            da['state'] = DriverState(da['state'])
            da['update_time'] = datetime.strptime(da['update_time'], '%Y-%m-%d %H:%M:%S.%f')
            driver_status = DriverStatus.from_dict(da)
            driver_allocations.append(driver_status)
        ride_infos = []
        for ri in ris:
            ri['ride_status'] = RideStatus(ri['state'])
            del ri['state']
            ri['last_location'] = Location.from_dict(ri['last_location'])
            ri['update_time'] = datetime.strptime(ri['update_time'], '%Y-%m-%d %H:%M:%S.%f')
            ride_info = RideInformation.from_dict(ri)
            ride_infos.append(ride_info)
        ride_wait_times = []
        for rwt in rwts:
            rwt['request_time'] = datetime.strptime(rwt['request_time'], '%Y-%m-%d %H:%M:%S.%f')
            rwt['wait_duration'] = timedelta(milliseconds=rwt['wait_duration'])
            rwt['location'] = Location.from_dict(rwt['location'])
            ride_wait_time = RideWaitInfo.from_dict(rwt)
            ride_wait_times.append(ride_wait_time)
        return driver_allocations, ride_infos, ride_wait_times


if __name__ == "__main__":
    app = App()
