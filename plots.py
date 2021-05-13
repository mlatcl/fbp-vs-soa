import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

SMALL_SIZE = 14
MEDIUM_SIZE = 18
LARGE_SIZE = 22
HEAD_WIDTH = 1
HEAD_LEN = 1
FAMILY = "Times New Roman"
plt.rc("font", size=SMALL_SIZE, family=FAMILY)
plt.rc("axes", titlesize=MEDIUM_SIZE, labelsize=MEDIUM_SIZE, linewidth=2.0)
plt.rc("xtick", labelsize=SMALL_SIZE)
plt.rc("ytick", labelsize=SMALL_SIZE)
plt.rc("legend", fontsize=SMALL_SIZE)
plt.rc("figure", titlesize=LARGE_SIZE)

data = pd.read_csv("metrics.csv")
metrics = ["halstead_volume", "halstead_difficulty", "halstead_effort", "maintainability_index",
           "cyclomatic_complexity", "cognitive_complexity"]

for metric in metrics:
    data_fbp = data.loc[data['app_key'].isin(["fbp_app_min", "fbp_app_data", "fbp_app_ml"])]
    data_soa = data.loc[data['app_key'].isin(["soa_app_min", "soa_app_data", "soa_app_ml"])]
    X = ["Min", "Data", "ML"]
    fig, ax = plt.subplots()
    sns.lineplot(data=data_fbp, x=X, y=metric, ax=ax, label="FBP-based", marker='o', markersize="8", linestyle=':')
    x = [0, 1, 2]
    y = data_fbp[metric].values
    u = np.diff(x)
    v = np.diff(y)
    pos_x = x[:-1] + u/2
    pos_y = y[:-1] + v/2
    norm = np.sqrt(u**2+v**2)
    ax.quiver(pos_x, pos_y, u/norm, v/norm, angles="xy", zorder=5, pivot="mid")
    sns.lineplot(data=data_soa, x=X, y=metric, ax=ax, label="SOA-based", marker='s', markersize="8", linestyle=':')
    y = data_soa[metric].values
    u = np.diff(x)
    v = np.diff(y)
    pos_x = x[:-1] + u/2
    pos_y = y[:-1] + v/2
    norm = np.sqrt(u**2+v**2)
    ax.quiver(pos_x, pos_y, u/norm, v/norm, angles="xy", zorder=5, pivot="mid")
    ax.set(xlabel="Application Stage", ylabel=metric.replace("_", " ").title())
    ax.grid(linestyle="-", linewidth="0.25", color="grey")
    ax.legend(title="Application Type", fancybox=True)
    plt.savefig("figs/"+metric+".pdf")

