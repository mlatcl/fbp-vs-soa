import requests

from playlist_builder.record_types import *

base_url = 'http://127.0.0.1:5000/'


class App():

    def evaluate(self):
        requests = self._load_unprocessed_requests()
        playlists = []
        for request in requests:
            movie_ids = self._filter_movies(request.genre)
            bonus_movie_id = self._get_bonus_movie()
            self._build_playlist(movie_ids, bonus_movie_id, request)
            playlist = self._load_playlist(request.id)
            playlists.append(playlist)
        return playlists

    def add_data(self, movies, playlist_requests):
        self._add_movies(movies)
        self._add_playlist_requests(playlist_requests)

    def _add_movies(self, movies):
        url = base_url + 'movie/add'
        # add a subset of movies to speed things up
        for movie in movies[:200]:
            response = requests.post(url, json=movie.to_dict())
            print(response.json())

    def _add_playlist_requests(self, playlist_requests):
        url = base_url + 'playlist/request/add'
        for playlist_request in playlist_requests:
            response = requests.post(url, json=playlist_request.to_dict())
            print(response.json())

    def _load_unprocessed_requests(self):
        url = base_url + 'playlist/request/all'
        response = requests.get(url, params={"is_processed": False})
        all_requests = [PlaylistRequest.from_dict(record) for record in response.json()]
        return all_requests

    def _filter_movies(self, genre):
        url = base_url + 'movie/filter'
        response = requests.get(url, params={"genre": genre})

        movie_ids = [int(id) for id in response.json()]
        return movie_ids

    def _get_bonus_movie(self):
        url = base_url + 'movie/bonus'
        response = requests.get(url)
        movie_id = int(response.text)
        return movie_id

    def _build_playlist(self, movie_ids, bonus_movie_id, request):
        url = base_url + 'playlist/build'
        params = {
            'movie_ids': movie_ids,
            'bonus_movie_id': bonus_movie_id,
            'count': request.count
        }
        response = requests.get(url, json=params)
        playlist_movie_ids = [int(id) for id in response.json()]

        url = base_url + 'playlist/save'
        params = {
            'request_id': request.id,
            'movie_ids': playlist_movie_ids
        }
        response = requests.post(url, json=params)

    def _load_playlist(self, request_id):
        url = base_url + 'playlist/load'
        response = requests.get(url, params={'request_id': request_id})
        playlist = MovieList.from_dict(response.json())
        return playlist