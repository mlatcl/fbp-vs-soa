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
