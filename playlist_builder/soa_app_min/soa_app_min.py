import requests

from playlist_builder.record_types import *

base_url = 'http://127.0.0.1:5000/'


class App():

    def evaluate(self):
        return []

    def add_data(self, movies, playlist_requests):
        self._add_movies(movies)
        self._add_playlist_requests(playlist_requests)

    def _add_movies(self, movies):
        url = base_url + 'movie/add'
        for movie in movies:
            response = requests.post(url, json=movie.to_dict())
            print(response.json())

    def _add_playlist_requests(self, playlist_requests):
        url = base_url + 'playlist_request/add'
        # for playlist_request in playlist_requests:
        #     response = requests.post(url, json=playlist_request.to_dict())
        #     print(response.json())