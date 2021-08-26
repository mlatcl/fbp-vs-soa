from typing import List, Dict, Callable, Tuple
from datetime import datetime

from flowpipe import Graph, INode, Node, InputPlug, OutputPlug
from mblogger.record_types import *


class Stream(INode):
    def __init__(self, **kwargs):
        super(Stream, self).__init__(**kwargs)
        self.data = []


    def add_data(self, new_data: List, key: Callable=None) -> None:
        if key is None:
            self.data.extend(new_data)
            return

        data_as_dict = {key(x):x for x in self.data}

        for record in new_data:
            # this may sometimes override existing records
            # but that's intentional as we only want one record per key
            data_as_dict[key(record)] = record

        self.data = list(data_as_dict.values())


    def get_data(self, drop=False):
        data_to_return = self.data[:]
        if drop:
            self.data = []
        return data_to_return


############ input streams ##############

class FollowRequestStream(Stream):
    def __init__(self, **kwargs):
        super(FollowRequestStream, self).__init__(**kwargs)
        OutputPlug('follow_requests', self)
    
    def compute(self) -> Dict:
        return {'follow_requests': self.data}


class CurrentFollowingsStream(Stream):
    def __init__(self, **kwargs):
        super(CurrentFollowingsStream, self).__init__(**kwargs)
        OutputPlug('followings', self)

    def compute(self) -> Dict:
        return {'followings': self.data}


class CurrentFollowersStream(Stream):
    def __init__(self, **kwargs):
        super(CurrentFollowersStream, self).__init__(**kwargs)
        OutputPlug('followers', self)

    def compute(self) -> Dict:
        return {'followers': self.data}


class PostsStream(Stream):
    def __init__(self, **kwargs):
        super(PostsStream, self).__init__(**kwargs)
        OutputPlug('posts', self)

    def compute(self) -> Dict:
        return {'posts': self.data}


############ output streams ##############

class UpdatedFollowingsStream(Stream):
    def __init__(self, **kwargs):
        super(UpdatedFollowingsStream, self).__init__(**kwargs)
        InputPlug('followings', self)
        OutputPlug('followings', self)

    def compute(self, followings: List) -> Dict:
        self.add_data(followings, lambda x: x.user_id)
        return {'followings': self.data}


class UpdatedFollowersStream(Stream):
    def __init__(self, **kwargs):
        super(UpdatedFollowersStream, self).__init__(**kwargs)
        InputPlug('followers', self)
        OutputPlug('followers', self)

    def compute(self, followers: List) -> Dict:
        self.add_data(followers, lambda x: x.user_id)
        return {'followers': self.data}


class TimelinesStream(Stream):
    def __init__(self, **kwargs):
        super(TimelinesStream, self).__init__(**kwargs)
        InputPlug('timelines', self)
        OutputPlug('timelines', self)

    def compute(self, timelines: List) -> Dict:
        self.add_data(timelines, lambda x: x.user_id)
        return {'timelines': self.data}


############ processing nodes ##############

class UpdateFollows(INode):
    def __init__(self, **kwargs):
        super(UpdateFollows, self).__init__(**kwargs)
        InputPlug('follow_requests', self)
        InputPlug('followings', self)
        InputPlug('followers', self)
        OutputPlug('followings', self)
        OutputPlug('followers', self)

    def compute(self, follow_requests: List[FollowRequest], followings: List[Tuple], followers: List[Tuple]) -> Dict:
        followings_as_dict = {x.user_id:x.followings for x in followings}
        followers_as_dict = {x.user_id:x.followers for x in followers}

        for request in follow_requests:
            active = request.active_author
            passive = request.passive_author

            if request.follow:
                followings_as_dict[active].add(passive)
                followers_as_dict[passive].add(active)
            else:
                followings_as_dict[active].discard(passive)
                followers_as_dict[passive].discard(active)

        return {
            'followings': [FollowingsRecord(user_id=key, followings=value) for key, value in followings_as_dict.items()],
            'followers': [FollowersRecord(user_id=key, followers=value) for key, value in followers_as_dict.items()]
        }


class BuildTimeline(INode):
    def __init__(self, **kwargs):
        super(BuildTimeline, self).__init__(**kwargs)
        InputPlug('posts', self)
        InputPlug('followings', self)
        OutputPlug('timelines', self)
    
    def compute(self, posts: List[Post], followings: List[FollowingsRecord]) -> Dict:
        timelines = []

        for user_followings in followings:
            user_id = user_followings.user_id
            following_ids = user_followings.followings

            posts_in_timeline = [post for post in posts if post.author_id in following_ids]
            posts_in_timeline.sort(key=lambda p: p.timestamp)

            timeline = Timeline(user_id=user_id, posts=posts_in_timeline)
            timelines.append(timeline)

        return {'timelines': timelines}


class App():
    def __init__(self):
        self._build()


    def evaluate(self):
        self.graph.evaluate()
        return self.get_outputs()

    def add_data(self, followings, followers, follow_requests, posts):
        self.input_streams['current_followings_stream'].add_data(followings, key=lambda x: x.user_id)
        self.input_streams['current_followers_stream'].add_data(followers, key=lambda x: x.user_id)
        self.input_streams['follow_request_stream'].add_data(follow_requests)
        self.input_streams['posts_stream'].add_data(posts, key=lambda x: x.post_id)


    def get_outputs(self):
        followers = self.output_streams["updated_followers_stream"].get_data(drop=True)
        followings = self.output_streams["updated_followings_stream"].get_data(drop=True)
        timelines = self.output_streams["timelines_stream"].get_data(drop=True)

        return followers, followings, timelines


    def _build(self) -> Graph:
        graph = Graph(name='MBlogger')

        # input streams
        follow_request_stream = FollowRequestStream(graph=graph)
        current_followings_stream = CurrentFollowingsStream(graph=graph)
        current_followers_stream = CurrentFollowersStream(graph=graph)
        posts_stream = PostsStream(graph=graph)
        self.input_streams = {
            'follow_request_stream': follow_request_stream,
            'current_followings_stream': current_followings_stream,
            'current_followers_stream': current_followers_stream,
            'posts_stream': posts_stream
        }

        # inner streams

        # output streams
        updated_followings_stream = UpdatedFollowingsStream(graph=graph)
        updated_followers_stream = UpdatedFollowersStream(graph=graph)
        timelines_stream = TimelinesStream(graph=graph)
        self.output_streams = {
            'updated_followings_stream': updated_followings_stream,
            'updated_followers_stream': updated_followers_stream,
            'timelines_stream': timelines_stream
        }

        # processing nodes
        update_follows = UpdateFollows(graph=graph)
        build_timeline = BuildTimeline(graph=graph)

        follow_request_stream.outputs["follow_requests"] >> update_follows.inputs["follow_requests"]
        current_followers_stream.outputs["followers"] >> update_follows.inputs["followers"]
        current_followings_stream.outputs["followings"] >> update_follows.inputs["followings"]

        update_follows.outputs["followings"] >> updated_followings_stream.inputs["followings"]
        update_follows.outputs["followers"] >> updated_followers_stream.inputs["followers"]

        posts_stream.outputs["posts"] >> build_timeline.inputs["posts"]
        updated_followings_stream.outputs["followings"] >> build_timeline.inputs["followings"]
        build_timeline.outputs["timelines"] >> timelines_stream.inputs["timelines"]

        self.graph = graph


if __name__ == "__main__":
    app = App()
    graph = app.graph

    print(graph.name)
    print(graph)
    print(graph.list_repr())