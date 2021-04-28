# Drivers information
from datetime import datetime, timedelta

from .ride import get_rides_by_state, update_ride

drivers = {}


# Add a new driver
def insert_driver(driver):
    driver_id = int(driver['driver_id'])
    drivers[driver_id] = driver
    return driver_id


# Insert/Update a dict of drivers
def insert_drivers(ds):
    affected = 0
    for driver in ds:
        if int(driver['driver_id']) not in drivers:
            insert_driver(driver)
            affected = affected + 1
        else:
            update_driver(int(driver['driver_id']), driver)
            affected = affected + 1
    return affected


# Update driver information
def update_driver(driver_id, driver):
    current_driver = drivers[driver_id]
    for key, value in driver.items():
        current_driver[key] = driver[key]
    drivers[driver_id] = current_driver
    return driver_id


# Get the list of drivers
def get_all_drivers():
    return drivers


# Get available drivers
def get_available_driver():
    for driver_id, driver in drivers.items():
        if driver['state'] == 'AVAILABLE':
            return driver
    return None

# Allocate drivers
def allocate_drivers():
    allocation = {}
    ride_infos = []
    driver_allocations = []
    ride_wait_times = []
    unassigned_rides = get_rides_by_state('UNASSIGNED')
    for ride in unassigned_rides:
        available_driver = get_available_driver()
        if available_driver is not None:
            available_driver['state'] = 'ASSIGNED'
            available_driver['update_time'] = str(datetime.now())
            drivers[available_driver['driver_id']] = available_driver
            ride['driver_id'] = available_driver['driver_id']
            ride['allocation_time'] = datetime.now()
            ride['update_time'] = datetime.now()
            ride['state'] = 'DRIVER_ASSIGNED'
            ride_info = {'driver_id': ride['driver_id'], 'allocation_time': ride['allocation_time'],
                         'update_time': ride['update_time'],'state': ride['state']}
            update_ride(ride['ride_id'], ride_info)
            ride_info['ride_id'] = ride['ride_id']
            ride_info['user_id'] = ride['user_id']
            ride_info['last_location'] = ride['last_location']
            del ride_info['allocation_time']
            ride_info['update_time'] = ride_info['update_time'].strftime('%Y-%m-%d %H:%M:%S.%f')
            ride_infos.append(ride_info)
            driver_status = {'driver_id': available_driver['driver_id'],
                             'update_time': available_driver['update_time'], 'state': available_driver['state']}
            driver_allocations.append(driver_status)
    enroute_rides = get_rides_by_state('ENROUTE')
    for ride in enroute_rides:
        ride_info = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'driver_id': ride['driver_id'],
                     'state': ride['state'], 'update_time': ride['update_time'], 'last_location': ride['last_location']}
        ride_infos.append(ride_info)
        request_time = datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f')
        wait_duration = ride['allocation_time'] - request_time
        wait_duration = wait_duration / timedelta(milliseconds=1)
        ride_wait_time = {'ride_id': ride['ride_id'], 'request_time': ride['request_time'],
                          'wait_duration': wait_duration, 'location': ride['last_location']}
        ride_wait_times.append(ride_wait_time)
    allocation['ride_infos'] = ride_infos
    allocation['driver_allocations'] = driver_allocations
    allocation['ride_wait_times'] = ride_wait_times
    return allocation

