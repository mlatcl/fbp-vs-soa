from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Movie:
    movie_title: str
    title_year: int
    genres: List[str]
    gross: int


@dataclass
class PlaylistRequest:
    id: int
    genre: str
    count: int


@dataclass
class MovieList:
    request_id: int
    movies: List[Movie]
