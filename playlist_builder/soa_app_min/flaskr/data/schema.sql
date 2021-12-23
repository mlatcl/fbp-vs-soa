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
  movie_count INTEGER NOT NULL
);
