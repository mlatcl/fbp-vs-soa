from random import choice, shuffle
from typing import Callable, Dict, List

import numpy as np

from flowpipe import INode, InputPlug, OutputPlug, Graph
from numpy.lib.function_base import quantile
from playlist_builder.record_types import *

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

class MoviesStream(Stream):
    def __init__(self, **kwargs):
        super(MoviesStream, self).__init__(**kwargs)
        OutputPlug('movies', self)

    def compute(self) -> Dict:
        return {'movies': self.data}


class PlaylistRequestStream(Stream):
    def __init__(self, **kwargs):
        super(PlaylistRequestStream, self).__init__(**kwargs)
        OutputPlug('new_requests', self)

    def compute(self) -> Dict:
        return {'new_requests': self.data}

############ inner streams ##############

class FilteredMoviesStream(Stream):
    def __init__(self, **kwargs):
        super(FilteredMoviesStream, self).__init__(**kwargs)
        InputPlug('filtered_movies', self)
        OutputPlug('filtered_movies', self)

    def compute(self, filtered_movies: List[MovieList]) -> Dict:
        self.add_data(filtered_movies, lambda x: x.request_id)
        return {'filtered_movies': self.data}

class BonusMovieStream(Stream):
    def __init__(self, **kwargs):
        super(BonusMovieStream, self).__init__(**kwargs)
        InputPlug('bonus_movies', self)
        OutputPlug('bonus_movies', self)

    def compute(self, bonus_movies: List[MovieList]) -> Dict:
        self.add_data(bonus_movies, lambda x: x.request_id)
        return {'bonus_movies': self.data}

class GenreStatsStream(Stream):
    def __init__(self, **kwargs):
        super(GenreStatsStream, self).__init__(**kwargs)
        InputPlug('genre_stats', self)
        OutputPlug('genre_stats', self)

    def compute(self, genre_stats: List[GenreStats]) -> Dict:
        self.add_data(genre_stats, lambda x: x.genre)
        return {'genre_stats': self.data}

############ output streams ##############

class PlaylistStream(Stream):
    def __init__(self, **kwargs):
        super(PlaylistStream, self).__init__(**kwargs)
        InputPlug('playlists', self)
        OutputPlug('playlists', self)

    def compute(self, playlists: List[MovieList]) -> Dict:
        self.add_data(playlists, lambda x: x.request_id)
        return {'playlists': self.data}


############ processing nodes ##############

class FilterMovies(INode):
    def __init__(self, **kwargs):
        super(FilterMovies, self).__init__(**kwargs)
        InputPlug('movies', self)
        InputPlug('requests', self)
        OutputPlug('filtered_movies', self)

    def compute(self, movies: List[Movie], requests: List[PlaylistRequest]) -> Dict:
        all_filtered_movies = []
        for request in requests:
            filtered_movies = [m for m in movies if request.genre in m.genres]
            shuffle(filtered_movies)
            all_filtered_movies.append(MovieList(request_id=request.id, movies=filtered_movies))

        return {'filtered_movies': all_filtered_movies}


class BonusMovie(INode):
    def __init__(self, **kwargs):
        super(BonusMovie, self).__init__(**kwargs)
        InputPlug('movies', self)
        InputPlug('requests', self)
        OutputPlug('bonus_movies', self)

    def compute(self, movies: List[Movie], requests: List[PlaylistRequest]) -> Dict:
        all_bonus_movies = []
        for request in requests:
            filtered_movies = [m for m in movies if request.genre not in m.genres]
            movie = choice(filtered_movies)
            all_bonus_movies.append(MovieList(request_id=request.id, movies=[movie]))

        return {'bonus_movies': all_bonus_movies}


class ComputeStatistics(INode):
    def __init__(self, **kwargs):
        super(ComputeStatistics, self).__init__(**kwargs)
        InputPlug('movies', self)
        OutputPlug('genre_stats', self)

    def compute(self, movies: List[Movie]) -> Dict:
        all_genres = [g for  m in movies for g in m.genres_list]
        all_genres = list(set(all_genres))

        points = np.array([0.25, 0.5, 0.75])

        all_genre_stats = []
        for genre in all_genres:
            movies_of_genre = [m for m in movies if genre in m.genres]
            movies_gross = np.array([m.gross for m in movies_of_genre], dtype=np.float64)
            quantiles = np.quantile(movies_gross, points)
            all_genre_stats.append(GenreStats(genre, quantiles))

        return {'genre_stats': all_genre_stats}


class BuildPlaylist(INode):
    def __init__(self, **kwargs):
        super(BuildPlaylist, self).__init__(**kwargs)
        InputPlug('filtered_movies', self)
        InputPlug('bonus_movies', self)
        InputPlug('requests', self)
        InputPlug('genre_stats', self)
        OutputPlug('playlists', self)

    def compute(self, filtered_movies: List[MovieList], bonus_movies: List[MovieList], requests: List[PlaylistRequest], genre_stats: List[GenreStats]) -> Dict:
        playlists = []
        for request in requests:
            filtered_per_request = next(f for f in filtered_movies if request.id == f.request_id)
            bonus_per_request = next(b for b in bonus_movies if request.id == b.request_id)

            playlist_movies = bonus_per_request.movies
            for m in filtered_per_request.movies:
                movie_genre_stats = [gs for gs in genre_stats if gs.genre in m.genres]
                # if movie is in top quantile for all of its genres, include it
                if all(float(m.gross) >= gs.quantiles[-1] for gs in movie_genre_stats):
                    playlist_movies.append(m)

            playlist_movies = playlist_movies[:request.count]
            playlists.append(MovieList(request_id=request.id, movies=playlist_movies))

        return {'playlists': playlists}


class App():
    def __init__(self):
        self._build()

    def evaluate(self):
        self.graph.evaluate()
        return self.get_outputs()

    def add_data(self, movies, playlist_requests):
        self.input_streams['movies_stream'].add_data(movies, key=lambda x: x.movie_title)
        self.input_streams['playlist_request_stream'].add_data(playlist_requests, key=lambda x: x.id)


    def get_outputs(self):
        playlists = self.output_streams["playlist_stream"].get_data(drop=True)
        return playlists


    def _build(self) -> Graph:
        graph = Graph(name='PlaylistBuilder')

        # input streams
        movies_stream = MoviesStream(graph=graph)
        playlist_request_stream = PlaylistRequestStream(graph=graph)
        self.input_streams = {
            'movies_stream': movies_stream,
            'playlist_request_stream': playlist_request_stream
        }

        # inner streams
        filtered_movies_stream = FilteredMoviesStream(graph=graph)
        bonus_movies_stream = BonusMovieStream(graph=graph)
        genre_stats_stream = GenreStatsStream(graph=graph)

        # output streams
        playlist_stream = PlaylistStream(graph=graph)
        self.output_streams = {
            'playlist_stream': playlist_stream
        }

        # processing nodes
        filter_movies = FilterMovies(graph=graph)
        bonus_movie = BonusMovie(graph=graph)
        compute_statistics = ComputeStatistics(graph=graph)
        build_playlist = BuildPlaylist(graph=graph)

        movies_stream.outputs["movies"] >> filter_movies.inputs["movies"]
        movies_stream.outputs["movies"] >> bonus_movie.inputs["movies"]
        playlist_request_stream.outputs["new_requests"] >> filter_movies.inputs["requests"]
        playlist_request_stream.outputs["new_requests"] >> bonus_movie.inputs["requests"]

        filter_movies.outputs["filtered_movies"] >> filtered_movies_stream.inputs["filtered_movies"]
        bonus_movie.outputs["bonus_movies"] >> bonus_movies_stream.inputs["bonus_movies"]

        filtered_movies_stream.outputs["filtered_movies"] >> build_playlist.inputs["filtered_movies"]
        bonus_movies_stream.outputs["bonus_movies"] >> build_playlist.inputs["bonus_movies"]
        playlist_request_stream.outputs["new_requests"] >> build_playlist.inputs["requests"]

        movies_stream.outputs["movies"] >> compute_statistics.inputs["movies"]
        compute_statistics.outputs["genre_stats"] >> genre_stats_stream.inputs["genre_stats"]
        genre_stats_stream.outputs["genre_stats"] >> build_playlist.inputs["genre_stats"]

        build_playlist.outputs["playlists"] >> playlist_stream.inputs["playlists"]

        self.graph = graph


if __name__ == "__main__":
    app = App()
    graph = app.graph

    print(graph.name)
    print(graph)
    print(graph.list_repr())
