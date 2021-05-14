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

data = pd.read_csv("metrics.csv", header=0)
only_numbers = data.loc[:, data.columns != "App Key"]
normalized_numbers = (only_numbers - only_numbers.min()) / (only_numbers.max() - only_numbers.min())

# this is for annotation of points on the scatter plot
point_labels = {
    0: {"txt": 'min', "x_shift": 0.03, "y_shift": 0.03},
    1: {"txt": 'data', "x_shift": 0.03, "y_shift": -0.03},
    2: {"txt": 'ml', "x_shift": -0.03, "y_shift": 0.03}
}

def plot_and_save(columns, plot_filename, legend_location):
    fig, ax = plt.subplots()
    markers = ['o', 's', '*']
    m_sizes = [8, 8, 12]
    m = 0
    for colname, col in normalized_numbers.iloc[:, columns].iteritems():
        fbp_values = col.loc[:2].tolist()
        soa_values = col.loc[3:].tolist()
        sns.lineplot(x=fbp_values, y=soa_values, ax=ax, label=colname, marker=markers[m], markersize=m_sizes[m], linestyle=':')
        u = np.diff(fbp_values)
        v = np.diff(soa_values)
        pos_x = fbp_values[:-1] + u / 2
        pos_y = soa_values[:-1] + v / 2
        norm = np.sqrt(u ** 2 + v ** 2)
        ax.quiver(pos_x, pos_y, u / norm, v / norm, angles="xy", zorder=5, pivot="mid")
        for i, (fv, sv) in enumerate(zip(fbp_values, soa_values)):
            ax.annotate(point_labels[i]['txt'], (fv+point_labels[i]['x_shift'], sv+point_labels[i]['y_shift']))
        m = m + 1

    plt.xlabel("FBP-based")
    plt.xlim(-0.1, 1.1)
    plt.ylabel("SOA-based")
    plt.ylim(-0.1, 1.1)
    plt.legend()
    ax.grid(linestyle="-", linewidth="0.25", color="grey")
    ax.legend(fancybox=True, loc=legend_location)

    plt.savefig(f"figs/{plot_filename}")

# sizes
plot_and_save([0, 1], "sizes.pdf", "lower right")
plot_and_save([2, 5, 6], "complexities.pdf", "best")


