from datetime import datetime

import fbp_app
import oop_app
from record_types import *
from generate_data import get_random_location, generate_requests, generate_init_driver_data, generate_ride_events


import random
random.seed(42)

app = fbp_app.App()
#app = oop_app.App()

n_drivers = 60
n_steps = 100
n_requests = 50
max_wait_steps = 10

requests = generate_requests(n_requests, n_steps)

driver_ids, driver_statuses, driver_locations = generate_init_driver_data(n_drivers)

ride_events_per_step = {}

# on each iteration there might be some data to drop from the input streams
data_to_drop = {}

# store new ride infos as they come up and feed them into the app
ride_info = []

for step in range(n_steps):
    print(f"################### Iteration {step} ###################")

    new_ride_requests = []
    if step in requests:
        new_ride_requests = [requests[step]]
    app.add_data(driver_statuses, driver_locations, new_ride_requests, ride_events_per_step.get(step, []), ride_info)


    driver_allocations, ride_info, ride_wait_time, estimated_wait_times = app.evaluate(save_dataset=False)
    print(estimated_wait_times)

    # for new rides that were allocated we need to generate events
    if len(ride_info) != 0:
        new_ride_events = generate_ride_events(ride_info, step, max_wait_steps)
        for event_step in new_ride_events:
            if event_step in ride_events_per_step:
                ride_events_per_step[event_step].extend(new_ride_events[event_step])
            else:
                ride_events_per_step[event_step] = new_ride_events[event_step]

    reserved_driver_ids = [da.driver_id for da in driver_allocations]
    for ds in driver_statuses:
        if ds.driver_id in reserved_driver_ids:
            ds.state = DriverState.ASSIGNED
