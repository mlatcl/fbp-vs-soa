from .db import get_db

# Create a new movie
def create_movie(movie):
    db = get_db()

    sql = 'INSERT INTO Movies (title, title_year, genres, gross)' \
          'VALUES (?, ?, ?, ?)'
    values = [movie['movie_title'], movie['title_year'], movie['genres'], movie['gross']]

    cursor = db.execute(sql, values)
    db.commit()
    return cursor.lastrowid


# filter movies by genre
def filter_movies(genre):
    db = get_db()

    sql = "SELECT movie_id from Movies WHERE genres LIKE ?"
    values = ['%' + genre + '%']

    movie_ids = []
    cursor = db.execute(sql, values)
    for row in cursor:
      movie_ids.append(row["movie_id"])

    return movie_ids


def get_random_movie():
    db = get_db()

    sql = "SELECT movie_id FROM Movies ORDER BY RANDOM() LIMIT 1;"
    cursor = db.execute(sql, ())
    row = next(cursor)
    movie_id = row["movie_id"]

    return movie_id