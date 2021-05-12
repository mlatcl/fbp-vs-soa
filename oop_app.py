########
# This code is here for posterity only.
# In the first version of the repo it was comparing FBP to OOP, where classes where used to emulate real services.
# Right now this code probably isn't compatible with main.py anymore, but we leave it here for posterity and reference.
########


from typing import List, Callable
from datetime import datetime
import jsonpickle
import json

from record_types import *


class DriverAllocationHandler():
    def __init__(self):
        self.driver_statuses = []
        self.driver_locations = []
        self.ride_requests = []
        self.current_ride_infos = []

    def add_data(self, driver_statuses, driver_locations, ride_requests, ride_infos):
        self.driver_statuses = self._add_data_by_key(self.driver_statuses, driver_statuses, lambda x: x.driver_id)
        self.driver_locations = self._add_data_by_key(self.driver_locations, driver_locations, lambda x: x.driver_id)
        self.ride_requests = self._add_data_by_key(self.ride_requests, ride_requests, lambda x: x.ride_id)
        self.current_ride_infos = self._add_data_by_key(self.current_ride_infos, ride_infos, lambda x: x.ride_id)

      
    def _add_data_by_key(self, current_data: List, new_data: List, key: Callable=None) -> None:
        if key is None:
            current_data.extend(new_data)
            return current_data

        data_as_dict = {key(x):x for x in current_data}

        for record in new_data:
            # this may sometimes override existing records
            # but that's ok as we only want one record per key
            data_as_dict[key(record)] = record

        return list(data_as_dict.values())


    ### merge all driver infos
    def _create_driver_info(self, last_status: DriverStatus, last_location: DriverLocation) -> DriverInformation:
        update_time = max(last_status.update_time, last_location.location_time)
        return DriverInformation(last_status.driver_id, last_status.state, last_location.location, update_time)

    def _create_all_driver_infos(self) -> List:
        all_driver_ids = {s.driver_id for s in self.driver_statuses} | {l.driver_id for l in self.driver_locations}
        all_driver_infos = []

        for driver_id in all_driver_ids:
            statuses = [s for s in self.driver_statuses if s.driver_id == driver_id]
            if not statuses:
                # status of the driver is unknown, dismiss
                continue
            locations = [l for l in self.driver_locations if l.driver_id == driver_id]
            if not locations:
                # location of the driver is unknown, dismiss
                continue

            current_status = max(statuses, key=lambda x: x.update_time)
            current_location = max(locations, key=lambda x: x.location_time)

            all_driver_infos.append(self._create_driver_info(current_status, current_location))

        return all_driver_infos

    def allocate_drivers(self):
        all_driver_infos = self._create_all_driver_infos()

        available_drivers = [di for di in all_driver_infos if di.last_state == DriverState.AVAILABLE]
        ride_allocations = []
        driver_allocations = []

        # filter out requests that weren't handled yet
        handled_ride_ids = [ride_info.ride_id for ride_info in self.current_ride_infos]
        new_ride_requests = [ride_request for ride_request in self.ride_requests if ride_request.ride_id not in handled_ride_ids]

        # at the moment we assume there are many more available drivers than requests
        for request in new_ride_requests:
            # just pick the first available driver
            driver = available_drivers[0]
            ride_info = RideInformation(request.ride_id, request.user_id,
                                        driver.driver_id, RideStatus.DRIVER_ASSIGNED,
                                        datetime.now(), request.from_location)
            ride_allocations.append(ride_info)

            driver_allocation = DriverStatus(driver.driver_id, datetime.now(), DriverState.ASSIGNED)
            driver_allocations.append(driver_allocation)

            # remove driver so that we don't do double allocation
            available_drivers = available_drivers[1:]
        
        # this change is needed to collect data
        # return driver_allocations, ride_allocations
        return driver_allocations, ride_allocations, all_driver_infos


class RideEventsHandler():
    def __init__(self):
        self.ride_events = []
    
    def add_data(self, ride_events):
        self.ride_events.extend(ride_events)

    def update_ride_info(self, ride_allocations):
        new_ride_infos = []
        for info in ride_allocations:
            for event in self.ride_events:
                if info.ride_id != event.ride_id:
                    continue

                updated_ride_info = self._update_ride_with_event(info, event)
                new_ride_infos.append(updated_ride_info)
                break

        return new_ride_infos


    def _update_ride_with_event(self, ride_info: RideInformation, ride_event: RideEvent) -> RideInformation:
        if (ride_event is None) or (ride_info.update_time > ride_event.event_time):
            return ride_info

        if ride_event.event_type == RideEventType.START:
            return RideInformation(ride_info.ride_id, ride_info.user_id, ride_info.driver_id,
                                   RideStatus.ENROUTE, ride_event.event_time, ride_event.event_data['location'])
        elif ride_event.event_type == RideEventType.LOCATION:
            return RideInformation(ride_info.ride_id, ride_info.user_id, ride_info.driver_id,
                                   ride_info.ride_status, ride_event.event_time, ride_event.event_data['location'])
        elif ride_event.event_type == RideEventType.COMPLETE:
            return RideInformation(ride_info.ride_id, ride_info.user_id, ride_info.driver_id,
                                   RideStatus.COMPLETED, ride_event.event_time, ride_event.event_data['location'])
        elif ride_event.event_type == RideEventType.CANCEL:
            return RideInformation(ride_info.ride_id, ride_info.user_id, ride_info.driver_id,
                                   RideStatus.CANCELLED, ride_event.event_time, ride_info.last_location)
        else:
            # unknown event type
            return ride_info


    def calculate_ride_wait_times(self, ride_requests):
        ride_starts = [ride_event for ride_event in self.ride_events if ride_event.event_type == RideEventType.START]

        wait_infos = []
        for ride_start in ride_starts:
            for ride_request in ride_requests:
                if ride_start.ride_id != ride_request.ride_id:
                    continue
                
                wait_duration = ride_start.event_time - ride_request.request_time
                wait_info = RideWaitInfo(ride_request.ride_id, ride_request.request_time, wait_duration, ride_request.from_location)
                wait_infos.append(wait_info)
                break

        return wait_infos


class App():
    def __init__(self):
        self.driver_allocation_handler = DriverAllocationHandler()
        self.ride_events_handler = RideEventsHandler()

    def add_data(self, driver_statuses, driver_locations, ride_requests, ride_events, ride_infos):
        self.driver_allocation_handler.add_data(driver_statuses, driver_locations, ride_requests, ride_infos)
        self.ride_events_handler.add_data(ride_events)

    def evaluate(self, save_dataset=False):
        dataset = {
            'AllocateRide': {
                'inputs': [],
                'outputs': []
            },
            'CalculateRideWaitTime': {
                'inputs': [],
                'outputs': []
            },
        }

        # this change is needed to collect data
        # driver_allocations, ride_allocations = self.driver_allocation_handler.allocate_drivers(latest_driver_infos)
        driver_allocations, ride_allocations, all_driver_infos = self.driver_allocation_handler.allocate_drivers()

        ride_infos = self.ride_events_handler.update_ride_info(ride_allocations)
        ride_wait_times = self.ride_events_handler.calculate_ride_wait_times(self.driver_allocation_handler.ride_requests)

        # all of these assignments need internal knowledge of exact implementation
        # this is no scalable - if we add another input or output, we need to add it here as well
        dataset['AllocateRide']['inputs'].extend(all_driver_infos)
        dataset['AllocateRide']['inputs'].extend(self.driver_allocation_handler.ride_requests)
        dataset['AllocateRide']['inputs'].extend(self.driver_allocation_handler.current_ride_infos)
        dataset['AllocateRide']['outputs'].extend(ride_allocations)
        dataset['AllocateRide']['outputs'].extend(driver_allocations)
        dataset['CalculateRideWaitTime']['inputs'].extend(self.ride_events_handler.ride_events)
        dataset['CalculateRideWaitTime']['inputs'].extend(self.driver_allocation_handler.ride_requests)
        dataset['CalculateRideWaitTime']['outputs'].extend(ride_wait_times)

        with open("dataset_oop_app.json", "a") as write_file:
            dataset_json = jsonpickle.encode(dataset, unpicklable=False, indent=2)
            write_file.write(dataset_json)

        # merge ride infos that were and were not updated with events
        new_ride_infos = {ra.ride_id:ra for ra in ride_allocations}
        for ri in ride_infos:
            new_ride_infos[ri.ride_id] = ri

        return driver_allocations, new_ride_infos.values(), ride_wait_times
