import sys
import random
import pandas as pd
import pathlib



from insurance_claims.fbp_app_min import App


random.seed(42)

n_steps = 5
n_claims_per_step = 5

# we know csv with input data is always near this file main.py is
# so here we retrieve main.py's directory here
# this way resulting path is the same regardless of how and where the file is executed
directory_path = pathlib.Path(__file__).parent.resolve()
input_data_df = pd.read_csv(directory_path.joinpath("insurance_claims.csv"))
input_data_df['claim_id'] = input_data_df.index
input_data = input_data_df.to_dict(orient='records')


app = App()
total_amount_claimed = 0.0


for step in range(n_steps):
    print(f"################### Iteration {step} ###################")

    print("--- Sampling input data ---")
    input_records = random.sample(input_data, n_claims_per_step)
    total_amount_claimed += sum([ir["total_claim_amount"] for ir in input_records])
    print(f"Total amount claimed: {total_amount_claimed}")

    print("--- Evaluating the app ---")
    app.add_data(input_records)
    claim_payouts = app.evaluate()

    print("--- Processing app output ---")
    total_amount_paid = sum([cp.payout for cp in claim_payouts])
    print(f"Total amount paid: {total_amount_paid}")
