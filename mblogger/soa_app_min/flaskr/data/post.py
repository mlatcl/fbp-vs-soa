from .db import get_db


# Creates a new post
def create_post(post):
    db = get_db()
    sql = 'INSERT INTO Posts (author_id, text) VALUES (?,?)'
    values = [post['author_id'], post['text']]
    cursor = db.execute(sql, values)
    db.commit()
    if cursor.rowcount == 0:
        return cursor.rowcount
    else:
        return cursor.lastrowid


# Gets a timeline
def get_timeline(author):
    res = []
    db = get_db()
    sql = 'SELECT * FROM Posts as p, Authors as a where p.author_id = ? and p.author_id = a.author_id'
    values = [author['author_id']]
    cursor = db.execute(sql, values)
    for post in cursor:
        r = {'post': post['post_id'], 'author': post['author_name'], 'text': post['text'],
             'time_stamp': post['time_stamp']}
        res.append(r)
    return res

