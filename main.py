import sys

from record_types import *
from generate_data import generate_requests, generate_init_driver_data, generate_ride_events

# importing all app implementations here
import fbp_app_min
import fbp_app_data
import fbp_app_ml
import soa_app_min
import soa_app_data
import soa_app_ml


all_apps = {
    "fbp_app_min": {
        "description": "FBP app that only provides basic functionality.",
        "create_app": (lambda: fbp_app_min.App()),
        "can_collect_data": False,
        "outputs_estimates": False
    },
    "fbp_app_data": {
        "description": "FBP app that is able to collect data.",
        "create_app": (lambda: fbp_app_data.App()),
        "can_collect_data": True,
        "outputs_estimates": False
    },
    "fbp_app_ml": {
        "description": "FBP app that outputs estimates of riding time with trained ML model.",
        "create_app": (lambda: fbp_app_ml.App()),
        "can_collect_data": True,
        "outputs_estimates": True
    },
    "soa_app_min": {
        "description": "SOA app that only provides basic functionality.",
        "create_app": (lambda: soa_app_min.App()),
        "can_collect_data": False,
        "outputs_estimates": False
    },
    "soa_app_data": {
        "description": "SOA app that is able to collect data.",
        "create_app": (lambda: soa_app_data.App()),
        "can_collect_data": True,
        "outputs_estimates": False
    },
    "soa_app_ml": {
        "description": "SOA app that outputs estimates of riding time with trained ML model.",
        "create_app": (lambda: soa_app_ml.App()),
        "can_collect_data": True,
        "outputs_estimates": True
    },
}

import random
random.seed(42)

if len(sys.argv) != 2 or sys.argv[1] not in all_apps.keys():
    print("Usage:")
    print("    python main.py <app_name>")
    print("List of available app names: " + " , ".join(all_apps.keys()))
    exit(1)

app_data = all_apps[sys.argv[1]]
app = app_data["create_app"]()
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

    if app_data["can_collect_data"]:
        output = app.evaluate(save_dataset=False)
    else:
        output = app.evaluate()

    if app_data["outputs_estimates"]:
        driver_allocations, ride_info, ride_wait_time, estimated_wait_times = output
        print(estimated_wait_times)
    else:
        driver_allocations, ride_info, ride_wait_time = output

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
