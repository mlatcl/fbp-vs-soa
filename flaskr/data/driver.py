# Drivers information

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


# Get a driver by ID
def get_driver(driver_id):
    if driver_id in drivers:
        driver = drivers[driver_id]
        driver['driver_id'] = driver_id
        return driver
    else:
        return None


# Get available drivers
def get_available_drivers():
    available_drivers = {}
    for driver_id, driver in drivers.items():
        if driver['last_state'] == 'AVAILABLE':
            available_drivers[driver_id] = driver
    return available_drivers


# Remove all drivers
def remove_all_drivers():
    drivers = {}
    return drivers

