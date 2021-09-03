import sys
import random
import pandas as pd
import pathlib

from insurance_claims import fbp_app_min
from insurance_claims import fbp_app_data
from insurance_claims import fbp_app_ml
from insurance_claims.soa_app_min import soa_app_min

directory_path = pathlib.Path(__file__).parent.resolve()
training_artifacts_dir_path = directory_path.joinpath("fbp_app_ml/training_artifacts")

all_apps = {
    "fbp_app_min": {
        "description": "FBP app that only provides basic functionality.",
        "create_app": (lambda: fbp_app_min.App()),
        "can_collect_data": False
    },
    "fbp_app_data": {
        "description": "FBP app that is able to collect data.",
        "create_app": (lambda: fbp_app_data.App()),
        "can_collect_data": True
    },
    "fbp_app_ml": {
        "description": "FBP app that replaces app logic with an ML model, while producing the same output.",
        "create_app": (lambda: fbp_app_ml.App(training_artifacts_dir_path)),
        "can_collect_data": False
    },
    "soa_app_min": {
        "description": "SOA app that only provides basic functionality.",
        "create_app": (lambda: soa_app_min.App()),
        "can_collect_data": False
    }
}

if len(sys.argv) != 2 or sys.argv[1] not in all_apps.keys():
    print("Usage:")
    print("    python main.py <app_name>")
    print("List of available app names: " + " , ".join(all_apps.keys()))
    exit(1)

app_data = all_apps[sys.argv[1]]

random.seed(42)

n_steps = 10
n_claims_per_step = 5

# we know csv with input data is always near this file main.py is
# so here we retrieve main.py's directory here
# this way resulting path is the same regardless of how and where the file is executed
input_data_df = pd.read_csv(directory_path.joinpath("insurance_claims.csv"))
input_data_df['claim_id'] = input_data_df.index
input_data = input_data_df.to_dict(orient='records')

total_amount_claimed = 0.0
total_amount_paid = 0.0

for step in range(n_steps):
    print(f"################### Iteration {step} ###################")

    print("--- Sampling input data ---")
    input_records = random.sample(input_data, n_claims_per_step)
    total_amount_claimed += sum([ir["total_claim_amount"] for ir in input_records])
    print(f"Total amount claimed: {total_amount_claimed}")

    print("--- Evaluating the app ---")
    app = app_data["create_app"]()
    app.add_data(input_records)
    if app_data["can_collect_data"]:
        claim_payouts = app.evaluate(save_dataset=True)
    else:
        claim_payouts = app.evaluate()

    print("--- Processing app output ---")
    total_amount_paid += sum([cp.payout for cp in claim_payouts])
    print(f"Total amount paid: {total_amount_paid}")
