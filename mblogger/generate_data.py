import random

from essential_generators import DocumentGenerator

from mblogger.record_types import *


def generate_requests(n_follow_requests, n_unfollow_requests, user_ids, followers):
    requests = []

    for _ in range(n_follow_requests):
        active, passive = random.sample(user_ids, 2)
        follow_request = FollowRequest(active_author=active, passive_author=passive, follow=True)
        requests.append(follow_request)
    
    for _ in range(n_unfollow_requests):
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


def generate_posts(n_new_posts, user_ids, post_id_offset):
    gen = DocumentGenerator()

    new_posts = []
    for _ in range(n_new_posts):
        text = gen.sentence()
        author_id = random.choice(user_ids)
        post_id = post_id_offset + len(new_posts) + 1
        post = Post(post_id, author_id, text, timestamp=datetime.now())
        new_posts.append(post)

    return new_posts
