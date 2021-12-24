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


# Load a movie
def load_by_id(movie_id):
    db = get_db()

    sql = 'SELECT * FROM Movies WHERE movie_id = ?'
    values = [movie_id]

    cursor = db.execute(sql, values)
    movie = next(cursor)
    return {
        "movie_id": movie["movie_id"],
        "title": movie["title"],
        "title_year": movie["title_year"],
        "genres": movie["genres"],
        "gross": movie["gross"]
    }


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


def get_all_genres():
    db = get_db()
    sql = "SELECT genres FROM Movies"
    cursor = db.execute(sql, ())

    genres = set()
    for row in cursor:
        row_genres = row["genres"].split("|")
        genres.update(row_genres)

    return genres


def get_gross(movie_ids):
    db = get_db()

    movie_ids_str = ",".join(str(x) for x in movie_ids)
    sql = f"SELECT gross FROM Movies WHERE movie_id IN ({movie_ids_str})"
    cursor = db.execute(sql, ())

    movies_gross = []
    for row in cursor:
        gross = int(row["gross"])
        movies_gross.append(gross)

    return movies_gross


def save_genre_stats(genre_stats):
    db = get_db()
    affected = 0

    sql = "INSERT INTO GenreStats (genre, quantile) VALUES (?, ?)"
    for quantile in genre_stats["quantiles"]:
        values = [genre_stats["genre"], quantile]
        db.execute(sql, values)
        db.commit()
        affected += 1

    return affected

def load_genre_stats(genre):
    db = get_db()

    sql = "SELECT genre, quantile FROM GenreStats WHERE genre = ? ORDER BY quantile"
    values = [genre]

    cursor = db.execute(sql, values)
    quantiles = []
    for row in cursor:
        quantiles.append(float(row["quantile"]))
    
    return {"genre": genre, "quantiles": quantiles}
