from typing import List, Dict, Callable
from datetime import datetime
import pandas as pd
import os.path
import pickle


from flowpipe import Graph, INode, Node, InputPlug, OutputPlug
from record_types import *


class Stream(INode):
    def __init__(self, **kwargs):
        super(Stream, self).__init__(**kwargs)
        self.data = []


    def add_data(self, new_data: List, key: Callable=None) -> None:
        if key is None:
            self.data.extend(new_data)
            return

        data_as_dict = {key(x):x for x in self.data}

        for record in new_data:
            # this may sometimes override existing records
            # but that's intentional as we only want one record per key
            data_as_dict[key(record)] = record

        self.data = list(data_as_dict.values())


    def get_data(self, drop=False):
        data_to_return = self.data[:]
        if drop:
            self.data = []
        return data_to_return


############# input streams ################

class DriverStatusStream(Stream):
    def __init__(self, **kwargs):
        super(DriverStatusStream, self).__init__(**kwargs)
        OutputPlug('driver_status', self)
    
    def compute(self) -> Dict:
        return {'driver_status': self.data}


class DriverLocationStream(Stream):
    def __init__(self, **kwargs):
        super(DriverLocationStream, self).__init__(**kwargs)
        OutputPlug('driver_location', self)

    def compute(self) -> Dict:
        return {'driver_location': self.data}


class RideRequestStream(Stream):
    def __init__(self, **kwargs):
        super(RideRequestStream, self).__init__(**kwargs)
        OutputPlug('ride_requests', self)

    def compute(self) -> Dict:
        return {'ride_requests': self.data}


class RideEventStream(Stream):
    def __init__(self, **kwargs):
        super(RideEventStream, self).__init__(**kwargs)
        OutputPlug('ride_events', self)
    
    def compute(self) -> Dict:
        return {'ride_events': self.data}


class CurrentRideInformationStream(Stream):
    def __init__(self, **kwargs):
        super(CurrentRideInformationStream, self).__init__(**kwargs)
        OutputPlug('current_ride_infos', self)
    
    def compute(self) -> Dict:
        return {'current_ride_infos': self.data}

############# inner streams ################
class DriverInformationStream(Stream):
    def __init__(self, **kwargs):
        super(DriverInformationStream, self).__init__(**kwargs)
        InputPlug('driver_info_stream', self)
        OutputPlug('driver_info_stream', self)
    
    def compute(self, driver_info_stream) -> Dict:
        self.add_data(driver_info_stream, lambda x: x.driver_id)
        return {'driver_info_stream': self.data}


class RideAllocationStream(Stream):
    def __init__(self, **kwargs):
        super(RideAllocationStream, self).__init__(**kwargs)
        InputPlug('ride_allocation_stream', self)
        OutputPlug('ride_allocation_stream', self)
    
    def compute(self, ride_allocation_stream) -> Dict:
        self.add_data(ride_allocation_stream, lambda x: x.ride_id)
        return {'ride_allocation_stream': self.data}


############# output streams ################

class UpdatedRideInformationStream(Stream):
    def __init__(self, **kwargs):
        super(UpdatedRideInformationStream, self).__init__(**kwargs)
        InputPlug('ride_info', self)
        InputPlug('ride_allocations', self)
        OutputPlug('ride_info', self)

    def compute(self, ride_info: List, ride_allocations: List) -> Dict:
        self.add_data(ride_info, lambda x: x.ride_id)
        self.add_data(ride_allocations, lambda x: x.ride_id)
        return {'ride_info': self.data}


class DriverAllocationStream(Stream):
    def __init__(self, **kwargs):
        super(DriverAllocationStream, self).__init__(**kwargs)
        InputPlug('driver_allocations', self)
        OutputPlug('driver_allocations', self)

    def compute(self, driver_allocations: List) -> Dict:
        self.add_data(driver_allocations)
        return {'driver_allocations': self.data}


class RideWaitTimeStream(Stream):
    def __init__(self, **kwargs):
        super(RideWaitTimeStream, self).__init__(**kwargs)
        InputPlug('ride_wait_times', self)
        OutputPlug('ride_wait_times', self)

    def compute(self, ride_wait_times: List) -> Dict:
        self.add_data(ride_wait_times)
        return {'ride_wait_times': self.data}


############# processing nodes ################

class JoinDriverInformation(INode):
    """
    Joins driver location and status to produce driver information records
    """
    def __init__(self, **kwargs):
        super(JoinDriverInformation, self).__init__(**kwargs)
        InputPlug('driver_status_stream', self)
        InputPlug('driver_location_stream', self)
        OutputPlug('driver_info_stream', self)

    def compute(self, driver_status_stream: List[DriverStatus], driver_location_stream: List[DriverLocation]) -> Dict:
        all_driver_ids = {s.driver_id for s in driver_status_stream} | {l.driver_id for l in driver_location_stream}
        all_infos = []

        for driver_id in all_driver_ids:
            statuses = [s for s in driver_status_stream if s.driver_id == driver_id]
            if not statuses:
                # status of the driver is unknown, dismiss
                continue
            locations = [l for l in driver_location_stream if l.driver_id == driver_id]
            if not locations:
                # location of the driver is unknown, dismiss
                continue

            current_status = max(statuses, key=lambda x: x.update_time)
            current_location = max(locations, key=lambda x: x.location_time)

            all_infos.append(self.get_driver_info(current_status, current_location))

        return {'driver_info_stream': all_infos}

    def get_driver_info(self, last_status: DriverStatus, last_location: DriverLocation) -> DriverInformation:
        update_time = max(last_status.update_time, last_location.location_time)
        return DriverInformation(last_status.driver_id, last_status.state, last_location.location, update_time)


class AllocateRide(INode):
    def __init__(self, **kwargs):
        super(AllocateRide, self).__init__(**kwargs)
        InputPlug('driver_info_stream', self)
        InputPlug('ride_request_stream', self)
        InputPlug('current_ride_info_stream', self)
        OutputPlug('ride_allocation_stream', self)
        OutputPlug('driver_allocation_stream', self)


    def compute(self, driver_info_stream: List[DriverInformation], ride_request_stream: List[RideRequest],
                current_ride_info_stream: List[RideInformation]) -> Dict:
        available_drivers = [di for di in driver_info_stream if di.last_state == DriverState.AVAILABLE]
        ride_infos = []
        driver_allocations = []

        # filter out requests that weren't handled yet
        handled_ride_ids = [ride_info.ride_id for ride_info in current_ride_info_stream]
        new_ride_requests = [ride_request for ride_request in ride_request_stream if ride_request.ride_id not in handled_ride_ids]

        # at the moment we assume there are many more available drivers than requests
        for request in new_ride_requests:
            # just pick the first available driver
            driver = available_drivers[0]
            ride_info = RideInformation(request.ride_id, request.user_id,
                                        driver.driver_id, RideStatus.DRIVER_ASSIGNED,
                                        datetime.now(), request.from_location)
            ride_infos.append(ride_info)

            driver_allocation = DriverStatus(driver.driver_id, datetime.now(), DriverState.ASSIGNED)
            driver_allocations.append(driver_allocation)

            # remove driver so that we don't do double allocation
            available_drivers = available_drivers[1:]

        return {'ride_allocation_stream': ride_infos, 'driver_allocation_stream': driver_allocations}


class UpdateRideInformation(INode):
    def __init__(self, **kwargs):
        super(UpdateRideInformation, self).__init__(**kwargs)
        InputPlug('ride_allocation_stream', self)
        InputPlug('ride_event_stream', self)
        OutputPlug('ride_info_stream', self)


    def compute(self, ride_allocation_stream: List[RideInformation], ride_event_stream: List[RideEvent]) -> Dict:
        ride_infos = []
        for info in ride_allocation_stream:
            for event in ride_event_stream:
                if info.ride_id != event.ride_id:
                    continue

                updated_ride_info = self.update_ride_info(info, event)
                ride_infos.append(updated_ride_info)
                break

        return {'ride_info_stream': ride_infos}


    def update_ride_info(self, ride_info: RideInformation, ride_event: RideEvent) -> RideInformation:
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


class CalculateRideWaitTime(INode):
    def __init__(self, **kwargs):
        super(CalculateRideWaitTime, self).__init__(**kwargs)
        InputPlug('ride_event_stream', self)
        InputPlug('ride_request_stream', self)
        OutputPlug('ride_wait_time_stream', self)


    def compute(self, ride_event_stream: List[RideEvent], ride_request_stream: List[RideRequest]) -> Dict:
        ride_starts = [ride_event for ride_event in ride_event_stream if ride_event.event_type == RideEventType.START]

        wait_infos = []
        for ride_start in ride_starts:
            for ride_request in ride_request_stream:
                if ride_start.ride_id != ride_request.ride_id:
                    continue
                
                wait_duration = ride_start.event_time - ride_request.request_time
                wait_info = RideWaitInfo(ride_request.ride_id, ride_request.request_time, wait_duration, ride_request.from_location)
                wait_infos.append(wait_info)
                break
        
        return {'ride_wait_time_stream': wait_infos}


class App():
    def __init__(self):
        self._build()


    def add_data(self, driver_statuses, driver_locations, ride_requests, ride_events, ride_infos):
        self.input_streams['driver_status_stream'].add_data(driver_statuses, key=lambda x: x.driver_id)
        self.input_streams['driver_location_stream'].add_data(driver_locations, key=lambda x: x.driver_id)
        self.input_streams['ride_request_stream'].add_data(ride_requests, key=lambda x: x.ride_id)
        self.input_streams['ride_event_stream'].add_data(ride_events)
        self.input_streams['current_ride_info_stream'].add_data(ride_infos)


    def evaluate(self):
        self.graph.evaluate()
        return self.get_outputs()

    def get_outputs(self):
        driver_allocations = self.output_streams['driver_allocation_stream'].get_data(drop=True)
        ride_infos = self.output_streams['updated_ride_info_stream'].get_data(drop=True)
        ride_wait_times = self.output_streams['ride_wait_time_stream'].get_data(drop=True)
        return driver_allocations, ride_infos, ride_wait_times


    def _build(self) -> Graph:
        graph = Graph(name='Ride sharing')

        # input streams
        driver_status_stream = DriverStatusStream(graph=graph)
        driver_location_stream = DriverLocationStream(graph=graph)
        ride_request_stream = RideRequestStream(graph=graph)
        ride_event_stream = RideEventStream(graph=graph)
        current_ride_info_stream = CurrentRideInformationStream(graph=graph)
        self.input_streams = {
            'driver_status_stream': driver_status_stream,
            'driver_location_stream': driver_location_stream,
            'ride_request_stream': ride_request_stream,
            'ride_event_stream': ride_event_stream,
            'current_ride_info_stream': current_ride_info_stream
        }

        # inner streams
        driver_info_stream = DriverInformationStream(graph=graph)
        ride_allocation_stream = RideAllocationStream(graph=graph)

        # output streams
        updated_ride_info_stream = UpdatedRideInformationStream(graph=graph)
        driver_allocation_stream = DriverAllocationStream(graph=graph)
        ride_wait_time_stream = RideWaitTimeStream(graph=graph)
        self.output_streams = {
            'updated_ride_info_stream': updated_ride_info_stream,
            'driver_allocation_stream': driver_allocation_stream,
            'ride_wait_time_stream': ride_wait_time_stream
        }

        # processing nodes
        join_driver_info = JoinDriverInformation(graph=graph)
        allocate_ride = AllocateRide(graph=graph)
        update_ride_information = UpdateRideInformation(graph=graph)
        calculate_ride_wait_time = CalculateRideWaitTime(graph=graph)

        driver_status_stream.outputs['driver_status'] >> join_driver_info.inputs['driver_status_stream']
        driver_location_stream.outputs['driver_location'] >> join_driver_info.inputs['driver_location_stream']
        current_ride_info_stream.outputs['current_ride_infos'] >> allocate_ride.inputs['current_ride_info_stream']
        join_driver_info.outputs['driver_info_stream'] >> driver_info_stream.inputs['driver_info_stream']
        driver_info_stream.outputs['driver_info_stream'] >> allocate_ride.inputs['driver_info_stream']
        ride_request_stream.outputs['ride_requests'] >> allocate_ride.inputs['ride_request_stream']
        allocate_ride.outputs['ride_allocation_stream'] >> ride_allocation_stream.inputs['ride_allocation_stream']
        ride_allocation_stream.outputs['ride_allocation_stream'] >> update_ride_information.inputs['ride_allocation_stream']
        ride_event_stream.outputs['ride_events'] >> update_ride_information.inputs['ride_event_stream']
        ride_event_stream.outputs['ride_events'] >> calculate_ride_wait_time.inputs['ride_event_stream']
        ride_request_stream.outputs['ride_requests'] >> calculate_ride_wait_time.inputs['ride_request_stream']
        allocate_ride.outputs['driver_allocation_stream'] >> driver_allocation_stream.inputs['driver_allocations']
        allocate_ride.outputs['ride_allocation_stream'] >> updated_ride_info_stream.inputs['ride_allocations']
        update_ride_information.outputs['ride_info_stream'] >> updated_ride_info_stream.inputs['ride_info']
        calculate_ride_wait_time.outputs['ride_wait_time_stream'] >> ride_wait_time_stream.inputs['ride_wait_times']

        self.graph = graph


if __name__ == "__main__":
    app = App()
    graph = app.graph

    print(graph.name)
    print(graph)
    print(graph.list_repr())
