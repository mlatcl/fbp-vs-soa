from .db import get_db
from datetime import datetime


# Creates a new post
def create_post(post):
    db = get_db()
    sql = 'INSERT INTO Posts (post_id, user_id, text, time_stamp) VALUES (?,?,?,?) ' \
          'ON CONFLICT(post_id) DO UPDATE SET text = ?'
    values = [post['post_id'], post['author_id'], post['text'],
              datetime.strptime(post['timestamp'], '%Y-%m-%d %H:%M:%S.%f'), post['text']]
    cursor = db.execute(sql, values)
    db.commit()
    if cursor.rowcount == 0:
        return cursor.rowcount
    else:
        return cursor.lastrowid


# Gets a timeline
def get_timelines():
    res = []
    users = []
    db = get_db()
    sql = 'SELECT DISTINCT user_id FROM Posts'
    cursor = db.execute(sql)

    for user in cursor:
        sql = 'SELECT * FROM Posts WHERE user_id = ?'
        values = [user['user_id']]
        posts = db.execute(sql,values)
        ps = []
        for post in posts:
            p = {'post_id': post['post_id'], 'author_id': post['user_id'], 'text': post['text'],
                 'timestamp': post['time_stamp'].strftime('%Y-%m-%d %H:%M:%S.%f')}
            ps.append(p)
        tl = {'user_id': user['user_id'], 'posts': ps}
        res.append(tl)
    return res

