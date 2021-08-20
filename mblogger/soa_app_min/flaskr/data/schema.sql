DROP TABLE IF EXISTS Follows;
DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS Authors;

CREATE TABLE Follows(
  active_author INTEGER NOT NULL,
  passive_author INTEGER NOT NULL,
  follow INTEGER NOT NULL,
  primary key(active_author, passive_author),
);

CREATE TABLE Posts(
  post_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  text TEXT NOT NULL,
  time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
);
