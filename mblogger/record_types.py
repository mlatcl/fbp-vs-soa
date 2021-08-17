from typing import List
from datetime import datetime


class Author:
    id: int
    name: str


class FollowRequest:
    active_author: int
    passive_author: int
    follow: bool


class FollowersRecord:
    user_id: int
    followers: List[int]


class FollowingsRecord:
    user_id: int
    followings: List[int]


class Post:
    post_id: int
    author_id: int
    text: str
    timestamp: datetime


class Timeline:
    user_id: int
    posts: List[Post]