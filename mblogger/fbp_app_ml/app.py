from typing import List, Dict, Callable, Tuple
from datetime import datetime
from collections import namedtuple

import random
import itertools as it

from flowpipe import Graph, INode, Node, InputPlug, OutputPlug
from mblogger.record_types import *

POST_START_WORD = "^"
PERSONAL_WORDS_WEIGHT = 10.0


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

class AuthorsStream(Stream):
    def __init__(self, **kwargs):
        super(AuthorsStream, self).__init__(**kwargs)
        OutputPlug('authors', self)
    
    def compute(self) -> Dict:
        return {'authors': self.data}


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


class GeneratePostsInputStream(Stream):
    def __init__(self, **kwargs):
        super(GeneratePostsInputStream, self).__init__(**kwargs)
        OutputPlug('generate_posts_input', self)

    def compute(self) -> Dict:
        return {'generate_posts_input': self.data}


############ internal streams ############
class PersonalDictionaryStream(Stream):
    def __init__(self, **kwargs):
        super(PersonalDictionaryStream, self).__init__(**kwargs)
        InputPlug('personal_dictionaries', self)
        OutputPlug('personal_dictionaries', self)

    def compute(self, personal_dictionaries: List[PersonalDictionary]) -> Dict:
        self.add_data(personal_dictionaries)
        return {'personal_dictionaries': self.data}


class NewBigramsStream(Stream):
    def __init__(self, **kwargs):
        super(NewBigramsStream, self).__init__(**kwargs)
        InputPlug('new_bigrams', self)
        OutputPlug('new_bigrams', self)

    def compute(self, new_bigrams: List[Tuple]) -> Dict:
        self.add_data(new_bigrams)
        return {'new_bigrams': self.data}


class BigramsStream(Stream):
    def __init__(self, **kwargs):
        super(BigramsStream, self).__init__(**kwargs)
        InputPlug('bigrams', self)
        OutputPlug('bigrams', self)

    def compute(self, bigrams: List[Tuple]) -> Dict:
        self.add_data(bigrams)
        return {'bigrams': self.data}


class BigramWeightsStream(Stream):
    def __init__(self, **kwargs):
        super(BigramWeightsStream, self).__init__(**kwargs)
        InputPlug('bigram_weights', self)
        OutputPlug('bigram_weights', self)

    def compute(self, bigram_weights: List[Tuple]) -> Dict:
        self.add_data(bigram_weights)
        return {'bigram_weights': self.data}

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


class GeneratedPostsStream(Stream):
    def __init__(self, **kwargs):
        super(GeneratedPostsStream, self).__init__(**kwargs)
        InputPlug('generated_posts', self)
        OutputPlug('generated_posts', self)

    def compute(self, generated_posts: List) -> Dict:
        self.add_data(generated_posts)
        return {'generated_posts': self.data}


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


class BuildPersonalDictionaries(INode):
    def __init__(self, **kwargs):
        super(BuildPersonalDictionaries, self).__init__(**kwargs)
        InputPlug('posts', self)
        OutputPlug('personal_dictionaries', self)

    def compute(self, posts: List[Post]) -> Dict:
        personal_dictionaries = {}

        for post in posts:
            user_id = post.author_id
            if user_id not in personal_dictionaries:
                personal_dictionaries[user_id] = set()
            
            text = post.text
            words = text.split(" ")
            for word in words:
                personal_dictionaries[user_id].add(word)

        output = [PersonalDictionary(user_id=k, words=v) for k, v in personal_dictionaries.items()]

        return {'personal_dictionaries': output}


class FindBigrams(INode):
    def __init__(self, **kwargs):
        super(FindBigrams, self).__init__(**kwargs)
        InputPlug('posts', self)
        OutputPlug('new_bigrams', self)
    

    def compute(self, posts: List[Post]):
        bigrams = []
        for post in posts:
            words = post.text.split(" ")
            words = [word for word in words if word]
            for bigram in zip(["^", *words], words):
                bigrams.append(bigram)
        
        return {'new_bigrams': bigrams}


class ProcessBigrams(INode):
    def __init__(self, **kwargs):
        super(ProcessBigrams, self).__init__(**kwargs)
        InputPlug('new_bigrams', self)
        OutputPlug('bigrams', self)
        OutputPlug('bigram_weights', self)

    def compute(self, new_bigrams: List[Tuple]) -> Dict:
        bigrams_dict = {}
        bigram_weights_dict = {}

        for lhs, rhs in new_bigrams:
            if lhs not in bigrams_dict:
                bigrams_dict[lhs] = set()
            bigrams_dict[lhs].add(rhs)

            if (lhs, rhs) not in bigram_weights_dict:
                bigram_weights_dict[lhs, rhs] = 0
            bigram_weights_dict[lhs, rhs] += 1

        bigrams = list(bigrams_dict.items())
        bigram_weights = list(bigram_weights_dict.items())

        return {'bigrams': bigrams, 'bigram_weights': bigram_weights}


class GeneratedPosts(INode):
    def __init__(self, **kwargs):
        super(GeneratedPosts, self).__init__(**kwargs)
        InputPlug('generate_posts_input', self)
        InputPlug('personal_dictionaries', self)
        InputPlug('bigrams', self)
        InputPlug('bigram_weights', self)
        OutputPlug('generated_posts', self)

    def compute(self,
                generate_posts_input: List[GeneratePostInput],
                personal_dictionaries: List[PersonalDictionary],
                bigrams: List[Tuple], bigram_weights: List[Tuple]) -> Dict:

        personal_dictionaries_dict = {x.user_id: x.words for x in personal_dictionaries}
        bigrams_dict = {lhs: rhs for lhs, rhs in bigrams}
        bigram_weights_dict = {bigram: weight for bigram, weight in bigram_weights}

        generated_posts = []
        for input_record in generate_posts_input:
            user_id = input_record.user_id
            if user_id not in personal_dictionaries_dict:
                # we don't have posts from this user yet, skip
                continue
            
            def word_generator():
                current_word = POST_START_WORD
                personal_words = personal_dictionaries_dict[user_id]
                while True:
                    next_words = list(bigrams_dict.get(current_word, []))
                    next_weights = [
                        (PERSONAL_WORDS_WEIGHT if next_word in personal_words else 1.0)
                        * bigram_weights_dict[current_word, next_word]
                        for next_word in next_words
                    ]
                    if not next_words:
                        return

                    next_word = random.choices(next_words, weights=next_weights)[0]
                    current_word = next_word
                    yield current_word

            text = " ".join(it.islice(word_generator(), input_record.length))
            post = Post(post_id=random.getrandbits(64), author_id=user_id, text=text, timestamp=datetime.now())
            generated_posts.append(post)
        
        return {"generated_posts": generated_posts}


class App():
    def __init__(self):
        self._build()


    def evaluate(self):
        self.graph.evaluate()
        return self.get_outputs()

    def add_data(self, followings, followers, follow_requests, posts, generate_posts_input):
        self.input_streams['current_followings_stream'].add_data(followings, key=lambda x: x.user_id)
        self.input_streams['current_followers_stream'].add_data(followers, key=lambda x: x.user_id)
        self.input_streams['follow_request_stream'].add_data(follow_requests)
        self.input_streams['posts_stream'].add_data(posts, key=lambda x: x.post_id)
        self.input_streams['generate_posts_input_stream'].add_data(generate_posts_input)

    def get_outputs(self):
        followers = self.output_streams["updated_followers_stream"].get_data(drop=True)
        followings = self.output_streams["updated_followings_stream"].get_data(drop=True)
        timelines = self.output_streams["timelines_stream"].get_data(drop=True)
        generated_posts = self.output_streams["generated_posts_stream"].get_data(drop=True)

        return followers, followings, timelines, generated_posts


    def _build(self) -> Graph:
        graph = Graph(name='MBlogger')

        # input streams
        follow_request_stream = FollowRequestStream(graph=graph)
        current_followings_stream = CurrentFollowingsStream(graph=graph)
        current_followers_stream = CurrentFollowersStream(graph=graph)
        posts_stream = PostsStream(graph=graph)
        generate_posts_input_stream = GeneratePostsInputStream(graph=graph)
        self.input_streams = {
            'follow_request_stream': follow_request_stream,
            'current_followings_stream': current_followings_stream,
            'current_followers_stream': current_followers_stream,
            'posts_stream': posts_stream,
            'generate_posts_input_stream': generate_posts_input_stream
        }

        # inner streams
        new_bigrams_stream = NewBigramsStream(graph=graph)
        bigrams_stream = BigramsStream(graph=graph)
        bigram_weights_stream = BigramWeightsStream(graph=graph)
        personal_dictionaries_stream = PersonalDictionaryStream(graph=graph)

        # output streams
        updated_followings_stream = UpdatedFollowingsStream(graph=graph)
        updated_followers_stream = UpdatedFollowersStream(graph=graph)
        timelines_stream = TimelinesStream(graph=graph)
        generated_posts_stream = GeneratedPostsStream(graph=graph)
        self.output_streams = {
            'updated_followings_stream': updated_followings_stream,
            'updated_followers_stream': updated_followers_stream,
            'timelines_stream': timelines_stream,
            'generated_posts_stream': generated_posts_stream,
        }

        # processing nodes
        update_follows = UpdateFollows(graph=graph)
        build_timeline = BuildTimeline(graph=graph)

        build_personal_dictionaries = BuildPersonalDictionaries(graph=graph)
        find_bigrams = FindBigrams(graph=graph)
        process_bigrams = ProcessBigrams(graph=graph)

        generate_posts = GeneratedPosts(graph=graph)


        # wiring up application
        follow_request_stream.outputs["follow_requests"] >> update_follows.inputs["follow_requests"]
        current_followers_stream.outputs["followers"] >> update_follows.inputs["followers"]
        current_followings_stream.outputs["followings"] >> update_follows.inputs["followings"]

        update_follows.outputs["followings"] >> updated_followings_stream.inputs["followings"]
        update_follows.outputs["followers"] >> updated_followers_stream.inputs["followers"]

        posts_stream.outputs["posts"] >> build_timeline.inputs["posts"]
        updated_followings_stream.outputs["followings"] >> build_timeline.inputs["followings"]
        build_timeline.outputs["timelines"] >> timelines_stream.inputs["timelines"]

        posts_stream.outputs["posts"] >> build_personal_dictionaries.inputs["posts"]
        build_personal_dictionaries.outputs["personal_dictionaries"] >> personal_dictionaries_stream.inputs["personal_dictionaries"]

        posts_stream.outputs["posts"] >> find_bigrams.inputs["posts"]
        find_bigrams.outputs["new_bigrams"] >> new_bigrams_stream.inputs["new_bigrams"]
        new_bigrams_stream.outputs["new_bigrams"] >> process_bigrams.inputs["new_bigrams"]
        process_bigrams.outputs["bigrams"] >> bigrams_stream.inputs["bigrams"]
        process_bigrams.outputs["bigram_weights"] >> bigram_weights_stream.inputs["bigram_weights"]

        generate_posts_input_stream.outputs["generate_posts_input"] >> generate_posts.inputs["generate_posts_input"]
        personal_dictionaries_stream.outputs["personal_dictionaries"] >> generate_posts.inputs["personal_dictionaries"]
        bigrams_stream.outputs["bigrams"] >> generate_posts.inputs["bigrams"]
        bigram_weights_stream.outputs["bigram_weights"] >> generate_posts.inputs["bigram_weights"]
        generate_posts.outputs["generated_posts"] >> generated_posts_stream.inputs["generated_posts"]

        self.graph = graph


if __name__ == "__main__":
    app = App()
    graph = app.graph

    print(graph.name)
    print(graph)
    print(graph.list_repr())