DROP TABLE IF EXISTS Follows;
DROP TABLE IF EXISTS Posts;
DROP TABLE IF EXISTS PersonalDictionaries;
DROP TABLE IF EXISTS Bigrams;

CREATE TABLE Follows(
  active_author INTEGER NOT NULL,
  passive_author INTEGER NOT NULL,
  follow INTEGER NOT NULL,
  primary key(active_author, passive_author)
);

CREATE TABLE Posts(
  post_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  text TEXT NOT NULL,
  type INTEGER,
  time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE PersonalDictionaries(
  user_id INTEGER NOT NULL,
  word TEXT NOT NULL,
  primary key(user_id, word)
);

CREATE TABLE Bigrams(
  first_word TEXT NOT NULL,
  second_word TEXT NOT NULL,
  weight INTEGER NOT NULL,
  primary key(first_word, second_word)
);
