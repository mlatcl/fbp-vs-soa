from .db import get_db
from datetime import datetime


# Creates a new post
def create_post(post):
    db = get_db()
    sql = 'INSERT INTO Posts (author_id, text) VALUES (?,?,?,?)'
    values = [post['post_id'], post['user_id'], post['text'],
              datetime.strptime(post['timestamp'], '%Y-%m-%d %H:%M:%S.%f')]
    cursor = db.execute(sql, values)
    db.commit()
    if cursor.rowcount == 0:
        return cursor.rowcount
    else:
        return cursor.lastrowid


# Gets a timeline
def get_timelines():
    res = []
    db = get_db()
    sql = 'SELECT DISTINCT user_id FROM Posts'
    users = db.execute(sql)
    for user in users:
        sql = 'SELECT * FROM Posts WHERE user_id = ?'
        values = [user]
        posts = db.execute(sql,values)
        for post in posts:
            r = {'post_id': post['post_id'], 'author_id': post['author_id'], 'text': post['text'],
                 'timestamp': post['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f')}
            res.append(r)
    return res

