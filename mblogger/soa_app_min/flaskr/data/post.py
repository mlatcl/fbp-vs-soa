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
    sql = 'SELECT DISTINCT active_author FROM Follows'
    cursor = db.execute(sql)
    for row in cursor:
        user = row['active_author']
        users.append(user)
    sql = 'SELECT DISTINCT passive_author FROM Follows'
    cursor = db.execute(sql)
    for row in cursor:
        user = row['passive_author']
        if user not in users:
            users.append(user)
    sql = 'SELECT DISTINCT user_id FROM Posts'
    cursor = db.execute(sql)
    for row in cursor:
        user = row['user_id']
        if user not in users:
            users.append(user)

    for user in users:
        sql = 'SELECT * FROM Posts WHERE user_id = ?'
        values = [user]
        posts = db.execute(sql,values)
        ps = []
        for post in posts:
            p = {'post_id': post['post_id'], 'author_id': post['user_id'], 'text': post['text'],
                 'timestamp': post['time_stamp'].strftime('%Y-%m-%d %H:%M:%S.%f')}
            ps.append(p)
        tl = {'user_id': user, 'posts': ps}
        res.append(tl)
    return res

