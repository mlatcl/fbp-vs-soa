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
def allocate_driver():
    available_driver = get_available_driver()
    if available_driver is not None:
        available_driver['state'] = 'ASSIGNED'
        available_driver['update_time'] = str(datetime.now())
        drivers[available_driver['driver_id']] = available_driver
        driver_status = {'driver_id': available_driver['driver_id'],
                         'update_time': available_driver['update_time'], 'state': available_driver['state']}
        return driver_status
    return None


# Release driver
def release_driver(driver_id):
    driver = drivers[driver_id]
    driver['state'] = 'AVAILABLE'
    driver['update_time'] = str(datetime.now())
    drivers[driver_id] = driver
