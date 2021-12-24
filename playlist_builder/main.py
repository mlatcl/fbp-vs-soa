import sys
import random
import csv

from playlist_builder.record_types import *

from playlist_builder import fbp_app_min
from playlist_builder import fbp_app_data
from playlist_builder import fbp_app_ml
from playlist_builder.soa_app_min import soa_app_min
from playlist_builder.soa_app_data import soa_app_data
from playlist_builder.soa_app_ml import soa_app_ml

all_apps = {
    "fbp_app_min": {
        "description": "FBP app that only provides basic functionality.",
        "create_app": (lambda: fbp_app_min.App())
    },
    "fbp_app_data": {
        "description": "FBP app that collects genre statistics.",
        "create_app": (lambda: fbp_app_data.App())
    },
    "fbp_app_ml": {
        "description": "FBP app that only recommends top grossing movies.",
        "create_app": (lambda: fbp_app_ml.App())
    },
    "soa_app_min": {
        "description": "SOA app that only provides basic functionality.",
        "create_app": (lambda: soa_app_min.App())
    },
    "soa_app_data": {
        "description": "SOA app that collects genre statistics.",
        "create_app": (lambda: soa_app_data.App())
    },
    "soa_app_ml": {
        "description": "SOA app that only recommends top grossing movies.",
        "create_app": (lambda: soa_app_ml.App())
    }
}


if len(sys.argv) != 2 or sys.argv[1] not in all_apps.keys():
    print("Usage:")
    print("    python main.py <app_name>")
    print("List of available app names: " + " , ".join(all_apps.keys()))
    exit(1)

print("--- Generating data ---")
all_movies = []
all_genres = []

import pathlib
directory_path = pathlib.Path(__file__).parent.resolve()
with open(directory_path.joinpath('movies.csv'), 'r') as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        movie = Movie(row[0], row[1], row[2], row[3])
        all_genres.extend(movie.genres_list)
        all_movies.append(movie)
all_genres = list(set(all_genres))

n_requests = 10
all_requests = []
for i in range(n_requests):
    r = PlaylistRequest(i, random.choice(all_genres), 5)
    all_requests.append(r)

app_data = all_apps[sys.argv[1]]
app = app_data["create_app"]()

app.add_data(all_movies, all_requests)
playlists = app.evaluate()

for p in playlists:
    print(p)
