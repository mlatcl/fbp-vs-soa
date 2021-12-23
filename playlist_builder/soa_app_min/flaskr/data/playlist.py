from .db import get_db

# Create a new request
def create_playlist_request(playlist_request):
    db = get_db()

    sql = 'INSERT INTO PlaylistRequests (id, genre, movie_count)' \
          'VALUES (?, ?, ?)'
    values = [playlist_request['id'], playlist_request['genre'], playlist_request['count']]

    cursor = db.execute(sql, values)
    db.commit()
    return cursor.lastrowid
