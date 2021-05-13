import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

SMALL_SIZE = 14
MEDIUM_SIZE = 18
LARGE_SIZE = 22
FAMILY = "Times New Roman"
plt.rc("font", size=SMALL_SIZE, family=FAMILY)
plt.rc("axes", titlesize=MEDIUM_SIZE, labelsize=MEDIUM_SIZE, linewidth=2.0)
plt.rc("xtick", labelsize=SMALL_SIZE)
plt.rc("ytick", labelsize=SMALL_SIZE)
plt.rc("legend", fontsize=SMALL_SIZE)
plt.rc("figure", titlesize=LARGE_SIZE)

metrics = pd.read_csv('metrics.csv')

metrics_fbp = metrics.loc[metrics['app_key'].isin(["fbp_app_min", "fbp_app_data", "fbp_app_ml"])]
metrics_soa = metrics.loc[metrics['app_key'].isin(["soa_app_min", "soa_app_data", "soa_app_ml"])]

fig, ax = plt.subplots()
sns.scatterplot(data=metrics_fbp, x=["Min", "Data", "ML"], y="halstead_volume", ax=ax, label="FBP-based")
sns.scatterplot(data=metrics_soa, x=["Min", "Data", "ML"], y="halstead_volume", ax=ax, label="SOA-based")
ax.set(xlabel="Application Stage", ylabel="Halstead Volume")
ax.grid(linestyle="-", linewidth="0.25", color="grey")
ax.legend(title="Application Type", fancybox=True)


plt.savefig("figs/fig.png")

