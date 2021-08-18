import sys
import random

from .fbp_app_min import App
from .record_types import *

random.seed(42)


n_steps = 5
n_users = 10
n_requests_per_step = 3
n_unfollows_per_step = 1


user_ids = [i for i in range(1, n_users + 1)]

followings = [FollowingsRecord(user_id=i, followings=set()) for i in user_ids]
followers = [FollowersRecord(user_id=i, followers=set()) for i in user_ids]
posts = []

def generate_requests():
    requests = []

    for _ in range(n_requests_per_step):
        active, passive = random.sample(user_ids, 2)
        follow_request = FollowRequest(active_author=active, passive_author=passive, follow=True)
        requests.append(follow_request)
    
    for _ in range(n_unfollows_per_step):
        followers_record = random.choice(followers)
        if len(followers_record.followers) == 0:
            # author has empty list of followers
            # no unfollow requests this time then
            break
        active = followers_record.user_id
        passive = random.choice(list(followers_record.followers))
        unfollow_request = FollowRequest(active_author=active, passive_author=passive, follow=False)
        
        requests.append(unfollow_request)

    return requests

app = App()

for step in range(n_steps):
    print(f"################### Iteration {step} ###################")
    for record in followers:
        print(f"User {record.user_id} has {len(record.followers)} followers")

    follow_requests = generate_requests()
    app.add_data(followings, followers, follow_requests, posts)
    output = app.evaluate()

    print()