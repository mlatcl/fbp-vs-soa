DROP TABLE IF EXISTS Movies;
DROP TABLE IF EXISTS PlaylistRequests;

CREATE TABLE Movies(
  movie_id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  title_year INTEGER NOT NULL,
  genres TEXT NOT NULL,
  gross INTEGER NOT NULL
);

CREATE TABLE PlaylistRequests(
  id INTEGER PRIMARY KEY,
  genre TEXT NOT NULL,
  movie_count INTEGER NOT NULL,
  is_processed INTEGER DEFAULT 0
);

CREATE TABLE Playlists(
  request_id INTEGER,
  movie_id INTEGER,
  FOREIGN KEY(request_id) REFERENCES PlaylistRequests(id),
  FOREIGN KEY(movie_id) REFERENCES Movies(movie_id)
)