import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

data = pd.read_csv("metrics.csv", header=0)
only_numbers = data.loc[:, data.columns != "App Key"]
normalized_numbers = (only_numbers - only_numbers.min()) / (only_numbers.max() - only_numbers.min())

# this is for annotation of points on the scatter plot
point_labels = {
    0: {"txt": 'min', "x_shift": 0.03, "y_shift": 0.03},
    1: {"txt": 'data', "x_shift": 0.03, "y_shift": -0.03},
    2: {"txt": 'ml', "x_shift": -0.03, "y_shift": 0.03}
}

def plot_and_save(columns, plot_filename):
    fig, ax = plt.subplots()

    for colname, col in normalized_numbers.iloc[:, columns].iteritems():
        fbp_values = col.loc[:2].tolist()
        soa_values = col.loc[3:].tolist()
        ax.scatter(fbp_values, soa_values, label=colname)
        for i, (fv, sv) in enumerate(zip(fbp_values, soa_values)):
            ax.annotate(point_labels[i]['txt'], (fv+point_labels[i]['x_shift'], sv+point_labels[i]['y_shift']))

    plt.xlabel("FBP")
    plt.xlim(-0.1, 1.1)
    plt.ylabel("SOA")
    plt.ylim(-0.1, 1.1)
    plt.legend()

    plt.savefig(f"figs/{plot_filename}")

# sizes
plot_and_save([0, 1], "sizes.pdf")
plot_and_save([2, 5, 6], "complexities.pdf")


