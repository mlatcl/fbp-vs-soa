import sys

from .fbp_app_min import App

n_steps = 5

app = App()

for step in range(n_steps):
    print(f"################### Iteration {step} ###################")

    # at each step we may have
    # 1. new users
    # 2. new follows
    # 3. new unfollows
    # 4. new posts

    app.add_data([], [], [], [])
    output = app.evaluate()

    print(output)