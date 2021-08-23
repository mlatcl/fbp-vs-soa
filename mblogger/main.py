import sys
import random
import datetime

from mblogger.fbp_app_min import App
#from mblogger.soa_app_min import soa_app_min
from mblogger.record_types import *

from essential_generators import DocumentGenerator

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

def generate_posts():
    gen = DocumentGenerator()

    new_posts = []
    for _ in range(n_posts_per_step):
        text = gen.sentence()
        author_id = random.choice(user_ids)
        post_id = len(posts) + len(new_posts) + 1
        post = Post(post_id, author_id, text, timestamp=datetime.now())
        new_posts.append(post)

    return new_posts

#app = soa_app_min.App()
app = App()

for step in range(n_steps):
    print(f"################### Iteration {step} ###################")

    print("--- Generating data ---")
    follow_requests = generate_requests()
    new_posts = generate_posts()
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
