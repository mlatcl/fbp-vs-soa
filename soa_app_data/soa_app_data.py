import requests
from record_types import RideStatus, DriverStatus, DriverState, Location, RideInformation, RideWaitInfo
from datetime import datetime, timedelta
import json

from record_types import *

base_url = 'http://127.0.0.1:5000/'


class App():

    def add_data(self, driver_statuses, driver_locations, ride_requests, ride_events, ride_infos):
        self.add_driver_statuses_data(driver_statuses)
        self.add_driver_locations_data(driver_locations)
        self.add_ride_data(ride_requests)
        self.add_ride_events(ride_events)
        self.add_ride_infos(ride_infos)

    # Client to add drivers status data
    def add_driver_statuses_data(self, driver_statuses):
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
    def add_driver_locations_data(self, driver_locations):
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
    def add_ride_data(self, ride_requests):
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
    def add_ride_events(self, ride_events):
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
    def add_ride_infos(self, ride_infos):
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

    def evaluate(self, save_dataset=True):
        driver_allocations = self.allocate_drivers()
        ride_infos = self.get_ride_infos()
        ride_wait_times = self.get_ride_wait_times()
        if save_dataset:
            self.save_dataset(ride_infos, ride_wait_times)
        return self.get_outputs(driver_allocations, ride_infos, ride_wait_times)

    # Client to allocate drivers
    def allocate_drivers(self):
        driver_allocations = []
        url = base_url + 'ride-request/get_rides_by_state'
        state = {'state': RideStatus.UNASSIGNED.value}
        response = requests.post(url, json=state)
        rides = response.json()
        for ride in rides:
            url = base_url + 'driver-request/allocate_driver'
            info = {'ride_id': ride['ride_id']}
            response = requests.post(url, json=info)
            driver_status = response.json()
            if driver_status is not None:
                url = base_url + 'ride-request/update_ride_allocation'
                info['driver_id'] = driver_status['driver_id']
                info['state'] = RideStatus.DRIVER_ASSIGNED.value
                response = requests.post(url, json=info)
                if response.status_code == 200:
                    driver_allocations.append(driver_status)
                else:
                    url = base_url + 'driver-request/release_driver'
                    info = {'ride_id': ride['ride_id']}
                    requests.post(url, json=info)
        return driver_allocations

    # Client to get ride infos
    def get_ride_infos(self):
        url = base_url + 'ride-request/get_ride_infos'
        response = requests.post(url, json={})
        # print(response.json())
        return response.json()

    # Client to get wait times
    def get_ride_wait_times(self):
        url = base_url + 'ride-request/get_ride_wait_times'
        response = requests.post(url, json={})
        # print(response.json())
        return response.json()

    # Save dataset function
    def save_dataset(self, ride_infos, ride_wait_times):
        if ride_infos != {}:
            ride_data_to_save = self._get_ride_data_to_save(ride_infos)
            dataset_records = []
            for ride_data in ride_data_to_save:
                driver_data_to_save = self._get_driver_data_to_save(ride_data['driver_id'])
                for key, value in driver_data_to_save.items():
                    ride_data[key] = value
                dataset_records.append(ride_data)
            self._save_data_to_file(dataset_records, 'allocate_ride_soa_app.csv')
        if ride_wait_times != {}:
            wait_times_data_to_save = self._get_wait_times_data_to_save(ride_wait_times)
            self._save_data_to_file(wait_times_data_to_save, 'wait_time_soa_app.csv')

    # Client to get ride data to save
    def _get_ride_data_to_save(self, ride_infos):
        url = base_url + 'data-request/get_ride_data_to_save'
        response = requests.post(url, json=ride_infos)
        ride_data = response.json()
        return ride_data

    # Client to get driver data to save
    def _get_driver_data_to_save(self, driver_id):
        url = base_url + 'driver-request/get_driver_data_to_save'
        response = requests.post(url, json={'driver_id': driver_id})
        driver_data = response.json()
        return driver_data

    # Client to get wait times data to save
    def _get_wait_times_data_to_save(self, ride_wait_times):
        url = base_url + 'data-request/get_wait_times_data_to_save'
        response = requests.post(url, json=ride_wait_times)
        wait_times_data = response.json()
        return wait_times_data

    # Client to save data
    def _save_data_to_file(self, info, file_name):
        url = base_url + 'data-request/save_data_to_file'
        content = {'info': info, 'file_name': file_name}
        requests.post(url, json=content)

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
