from .db import get_db

# Create a new request
def create_playlist_request(playlist_request):
    db = get_db()

    sql = 'INSERT OR IGNORE INTO PlaylistRequests (id, genre, movie_count) ' \
          'VALUES (?, ?, ?) '
    values = [playlist_request['id'], playlist_request['genre'], playlist_request['count']]

    cursor = db.execute(sql, values)
    db.commit()
    return cursor.lastrowid

# Load requests
def get_playlist_requests(is_processed=None):
    db = get_db()

    sql = 'SELECT id, genre, movie_count, is_processed FROM PlaylistRequests'
    values = []
    if is_processed is not None:
        sql += ' WHERE is_processed = ?'
        values = [1] if is_processed else [0]

    res = []
    cursor = db.execute(sql, values)
    for row in cursor:
        pr = {'id': row['id'], 'genre': row['genre'], 'count': row['movie_count']}
        res.append(pr)
    return res


def save_playlist(playlist):
    db = get_db()
    affected = 0

    sql = 'INSERT INTO Playlists (request_id, movie_id) VALUES (?, ?)'
    request_id = int(playlist["request_id"])
    for movie_id in playlist["movie_ids"]:
        values = [request_id, int(movie_id)]
        db.execute(sql, values)
        db.commit()
        affected += 1
    
    return affected


def load_playlist_movies(request_id):
    db = get_db()

    sql = 'SELECT m.* FROM Movies m ' \
          'INNER JOIN Playlists p ON m.movie_id = p.movie_id ' \
          'WHERE p.request_id = ?'
    values = [request_id]

    cursor = db.execute(sql, values)

    movies = []
    for row in cursor:
        movie = {
            'movie_title': row["title"],
            'title_year': row["title_year"],
            'genres': row["genres"],
            'gross': row["gross"]
        }
        movies.append(movie)

    return movies
