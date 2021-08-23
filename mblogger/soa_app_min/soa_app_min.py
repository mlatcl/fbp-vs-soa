import requests

from mblogger.record_types import *

base_url = 'http://127.0.0.1:5000/'


class App():

    def evaluate(self):
        followers = self._get_followers()
        followings = self._get_followings()
        timelines = self._get_timelines()
        return self.get_outputs(followers, followings, timelines)

    # Client to get list of followers
    def _get_followers(self):
        url = base_url + 'author-request/list_followers'
        response = requests.post(url, json={})
        followers = response.json()
        return followers

    # Client to get list of followings
    def _get_followings(self):
        url = base_url + 'author-request/list_followings'
        response = requests.post(url, json={})
        followings = response.json()
        return followings

    # Client to get list of followings
    def _get_timelines(self):
        url = base_url + 'post-request/get_timelines'
        response = requests.post(url, json={})
        followings = response.json()
        return followings

    def add_data(self, followings, followers, follow_requests, posts):
        self._add_follow_requests(follow_requests)
        self._add_posts(posts)

    # Client to add follows data
    def _add_follow_requests(self, follow_requests):
        if len(follow_requests) > 0:
            follows = []
            for follow in follow_requests:
                f = follow.to_dict()
                follows.append(f)
            url = base_url + 'author-request/follows'
            response = requests.post(url, json=follows)
            # print(response.json())

    # Client to add follows data
    def _add_posts(self, posts):
        if len(posts) > 0:
            ps = []
            for post in posts:
                p = post.to_dict()
                p['timestamp'] = str(post.timestamp)
                ps.append(p)
            url = base_url + 'post-request/create_posts'
            response = requests.post(url, json=ps)
            # print(response.json())

    # Parsing data for main program
    def get_outputs(self, followers, followings, timelines):
        followers = self._parse_followers(followers)
        followings = self._parse_followings(followings)
        timelines = self._parse_timelines(timelines)
        return followers, followings, timelines

    # Parses followers
    def _parse_followers(self, followers):
        fs = []
        for follower in followers:
            fls = follower['followers']
            f = FollowersRecord.from_dict(follower)
            f.followers = fls
            fs.append(f)
        return fs

    # Parses followings
    def _parse_followings(self, followings):
        fs = []
        for following in followings:
            fls = following['followings']
            f = FollowingsRecord.from_dict(following)
            f.followings = fls
            fs.append(f)
        return fs

    # Parses timelines
    def _parse_timelines(self, timelines):
        ts = []
        for timeline in timelines:
            posts = timeline['posts']
            for post in posts:
                post['timestamp'] = datetime.strptime(post['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
            timeline['posts'] = posts
            t = Timeline.from_dict(timeline)
            ts.append(t)
        return ts


if __name__ == "__main__":
    app = App()
