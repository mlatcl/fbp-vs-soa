from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Movie:
    movie_title: str
    title_year: int
    genres: str
    gross: int

    @property
    def genres_list(self) -> List[str]:
        return self.genres.split("|")


@dataclass_json
@dataclass
class PlaylistRequest:
    id: int
    genre: str
    count: int


@dataclass_json
@dataclass
class MovieList:
    request_id: int
    movies: List[Movie]


@dataclass
class GenreStats:
    genre: str
    quantiles: List[float]