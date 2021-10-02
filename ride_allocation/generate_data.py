import sys
import random
from datetime import datetime, timedelta

from .record_types import *


def generate_driver_ids(n=10):
    return random.sample(range(1, sys.maxsize), n)


def generate_user_ids(n=100):
    return random.sample(range(1, sys.maxsize), n)


def get_random_location():
    random_lat = 100*random.random()
    random_lon = 100*random.random()
    return Location(lat=random_lat, lon=random_lon)


def generate_requests(n_requests, n_steps):
    steps = random.sample(range(n_steps), n_requests)

    requests = {
        step: RideRequest(step, step, datetime.now(), get_random_location(), get_random_location())
        for step in steps
    }

    return requests


def generate_init_driver_data(n_drivers):
    driver_ids = list(range(n_drivers))
    driver_statuses = [DriverStatus(driver_id, datetime.now(), DriverState.AVAILABLE) for driver_id in driver_ids]
    driver_locations = [DriverLocation(driver_id, datetime.now(), get_random_location()) for driver_id in driver_ids]

    return driver_ids, driver_statuses, driver_locations


def generate_ride_events(ride_info, current_step, max_wait_steps):
    ride_events = {}
    for ri in ride_info:
        wait_steps = random.randint(1, max_wait_steps)
        ride_event = RideEvent(ri.ride_id, event_time=datetime.now() + timedelta(minutes=wait_steps),
                               event_type=RideEventType.START,
                               event_data={'location': get_random_location()})
        event_step = current_step + wait_steps
        if event_step in ride_events:
            ride_events[event_step].append(ride_event)
        else:
            ride_events[event_step] = [ride_event]
    
    return ride_events
