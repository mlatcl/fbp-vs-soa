import pickle
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn import preprocessing


claim_complexity_df = pd.read_csv("../claim_complexity.csv")
claim_complexity_df = claim_complexity_df.drop_duplicates(subset=["claim_id"])
claim_complexity_df.set_index('claim_id', inplace=True)

# some columns in the dataset are objects and need to be encoded
le = preprocessing.LabelEncoder()
for column_name in claim_complexity_df.columns:
    if claim_complexity_df[column_name].dtype == object:
        claim_complexity_df[column_name] = le.fit_transform(claim_complexity_df[column_name])

    # we now need to save these trained encoders to be able to reuse them during prediction
    file_name = f"training_artifacts/{column_name}_encoder.obj"
    with open(file_name, "wb") as f:
        pickle.dump(le, f)

X = claim_complexity_df.drop("is_complex", axis=1)
y = claim_complexity_df["is_complex"]

# max depth here cripples the tree algorithm a bit
# so that it isn't perfect
model = DecisionTreeClassifier(max_depth=2).fit(X, y)
print("Prediction score: ", model.score(X, y))

with open("training_artifacts/fbp_model.obj", "wb") as f:
    pickle.dump(model, f)

