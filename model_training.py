import pickle
import pandas as pd
from sklearn.linear_model import LinearRegression

allocation_df = pd.read_csv("allocate_ride_fbp_app.csv", header=0)
allocation_df = allocation_df.drop_duplicates(subset=["ride_id"])
allocation_df.set_index('ride_id', inplace=True)

wait_time_df = pd.read_csv("wait_time_fbp_app.csv", header=0)
wait_time_df = wait_time_df.drop_duplicates(subset=["ride_id"])
wait_time_df.set_index("ride_id", inplace=True)

dataset_df = allocation_df.join(wait_time_df, how="left")
dataset_df = dataset_df.dropna()

X = dataset_df[["driver_lat", "driver_lon", "user_lat", "user_lon"]]
y = pd.to_timedelta(dataset_df["wait_duration"]).dt.seconds

model = LinearRegression().fit(X, y)
print("MAE: ", (model.predict(X) - y).abs().mean())
print("MSE: ", (model.predict(X) - y).pow(2).mean())

with open("fbp_model.obj", "wb") as f:
    pickle.dump(model, f)
