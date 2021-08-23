from typing import List, Set
from datetime import datetime
from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass
class Author:
    id: int
    name: str

@dataclass_json
@dataclass
class FollowRequest:
    active_author: int
    passive_author: int
    follow: bool

@dataclass_json
@dataclass
class FollowersRecord:
    user_id: int
    followers: Set[int]

@dataclass_json
@dataclass
class FollowingsRecord:
    user_id: int
    followings: Set[int]

@dataclass_json
@dataclass
class Post:
    post_id: int
    author_id: int
    text: str
    timestamp: datetime

@dataclass_json
@dataclass
class Timeline:
    user_id: int
    posts: List[Post]


@dataclass_json
@dataclass
class PersonalDictionary:
    user_id: int
    words: set


@dataclass_json
@dataclass
class GeneratePostInput:
    # which user to generate the post for
    user_id: int
    # length of post in words
    length: int