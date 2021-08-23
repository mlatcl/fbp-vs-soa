import sys
import random
import datetime

from mblogger.record_types import *
from mblogger.generate_data import generate_requests, generate_posts

from mblogger import fbp_app_min
from mblogger import fbp_app_data
from mblogger.soa_app_min import soa_app_min


all_apps = {
    "fbp_app_min": {
        "description": "FBP app that only provides basic functionality.",
        "create_app": (lambda: fbp_app_min.App())
    },
    "fbp_app_data": {
        "description": "FBP app that is able to collect data.",
        "create_app": (lambda: fbp_app_data.App())
    },
    "soa_app_min": {
        "description": "SOA app that only provides basic functionality.",
        "create_app": (lambda: soa_app_min.App())
    }
}

random.seed(42)


n_steps = 5
n_users = 10

n_requests_per_step = 3
n_unfollows_per_step = 1
n_posts_per_step = 3


user_ids = [i for i in range(1, n_users + 1)]

followings = [FollowingsRecord(user_id=i, followings=set()) for i in user_ids]
followers = [FollowersRecord(user_id=i, followers=set()) for i in user_ids]
posts = []


if len(sys.argv) != 2 or sys.argv[1] not in all_apps.keys():
    print("Usage:")
    print("    python main.py <app_name>")
    print("List of available app names: " + " , ".join(all_apps.keys()))
    exit(1)

app_data = all_apps[sys.argv[1]]
app = app_data["create_app"]()


for step in range(n_steps):
    print(f"################### Iteration {step} ###################")

    print("--- Generating data ---")
    follow_requests = generate_requests(n_requests_per_step, n_unfollows_per_step, user_ids, followers)
    new_posts = generate_posts(n_posts_per_step, user_ids, len(posts))
    posts.extend(new_posts)
    app.add_data(followings, followers, follow_requests, posts)

    print("--- Evaluation ---")
    followers, followings, timelines = app.evaluate()

    print("--- Stats after evaluation ---")
    for user_id in user_ids:
        f = 0
        p = 0
        try:
            record = next(r for r in followings if r.user_id == user_id)
            f = len(record.followings)
        except StopIteration:
            f = 0
        try:
            timeline = next(t for t in timelines if t.user_id == user_id)
            p = len(timeline.posts)
        except StopIteration:
            p = 0
        print(f"User {user_id} follows {f} users and has {p} posts in timeline")

    print()
