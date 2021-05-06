# Drivers information
from datetime import datetime, timedelta

drivers = {}


# Add a new driver
def insert_driver(driver):
    driver_id = int(driver['driver_id'])
    if driver_id not in drivers:
        drivers[driver_id] = driver
        return True
    else:
        return False


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


# Release driver
def release_driver(driver_id):
    driver = drivers[driver_id]
    driver['state'] = 'AVAILABLE'
    driver['update_time'] = str(datetime.now())
    drivers[driver_id] = driver


# Get driver data to save
def get_driver_data_to_save(driver_id):
    res = {}
    driver = drivers[driver_id]
    res['driver_id'] = driver_id
    res['driver_lat'] = driver['location']['lat']
    res['driver_lon'] = driver['location']['lon']
    return res


# Get driver by id
def get_driver_by_id(driver_id):
    if driver_id in drivers:
        return drivers[driver_id]
    else:
        return None