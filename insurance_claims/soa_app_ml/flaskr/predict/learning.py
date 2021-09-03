import os
import pickle

import pandas as pd

training_artifacts_dir_path = '../training_artifacts/'

# Predicts claims complexity
def predict_claims_complexity(claims):
    model_path = training_artifacts_dir_path.joinpath("fbp_model.obj")
    model = None
    if os.path.isfile(model_path):
        with open(model_path, "rb") as f:
            model = pickle.load(f)
    else:
        raise ValueError(f"Model file not found at {model_path}")

    df = pd.DataFrame.from_records(claims)
    df.set_index('claim_id', inplace=True)
    for column_name in df.columns:
        if df[column_name].dtype == object:
            # load LabelEncoder and encode column
            file_name = training_artifacts_dir_path.joinpath(f"{column_name}_encoder.obj")
            with open(file_name, "rb") as f:
                le = pickle.load(f)
            df[column_name] = le.transform(df[column_name])
    y = model.predict(df)

    complex_claims = []
    simple_claims = []
    for claim, is_complex in zip(claims, y):
        if is_complex:
            complex_claims.append(claim)
        else:
            simple_claims.append(claim)

    return {"simple_claims": simple_claims, "complex_claims": complex_claims}