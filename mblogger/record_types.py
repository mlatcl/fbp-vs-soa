from typing import List, Set
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Author:
    id: int
    name: str

@dataclass
class FollowRequest:
    active_author: int
    passive_author: int
    follow: bool

@dataclass
class FollowersRecord:
    user_id: int
    followers: Set[int]

@dataclass
class FollowingsRecord:
    user_id: int
    followings: Set[int]

@dataclass
class Post:
    post_id: int
    author_id: int
    text: str
    timestamp: datetime

@dataclass
class Timeline:
    user_id: int
    posts: List[Post]