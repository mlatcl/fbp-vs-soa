DROP TABLE IF EXISTS Follows;
DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS Authors;

CREATE TABLE Authors(
  author_id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_name TEXT NOT NULL
);

CREATE TABLE Follows(
  active_author INTEGER NOT NULL,
  passive_author INTEGER NOT NULL,
  primary key(active_author, passive_author),
  foreign key(active_author) REFERENCES Authors(author_id),
  foreign key(passive_author) REFERENCES Authors(author_id)
);

CREATE TABLE Posts(
  post_id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  text TEXT NOT NULL,
  time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  foreign key(author_id) REFERENCES Authors(author_id)
);
