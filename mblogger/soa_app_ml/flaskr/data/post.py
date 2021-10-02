from .db import get_db
from datetime import datetime
import random
from .text_generator import TextGenerator


# Creates a new post
def create_post(post):
    db = get_db()
    sql = 'INSERT INTO Posts (post_id, user_id, text, type, time_stamp) VALUES (?,?,?,0,?) ' \
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


# Gets generated posts
def get_generated_posts():
    res = []
    db = get_db()
    sql = 'SELECT * FROM Posts WHERE type = 1'
    cursor = db.execute(sql)
    for post in cursor:
        p = {'post_id': post['post_id'], 'author_id': post['user_id'], 'text': post['text'],
             'timestamp': post['time_stamp'].strftime('%Y-%m-%d %H:%M:%S.%f')}
        res.append(p)
    return res


# Creates Generated post
def generate_post(req):
    user_id = req['user_id']
    length = req['length']

    db = get_db()
    sql = 'SELECT first_word FROM Bigrams'
    cursor = db.execute(sql)
    bigram_weights = []
    for row in cursor:
        bigram = {'first_word': row['first_word'], 'second_word': row['second_word'], 'weight': row['weight']}
        bigram_weights.append(bigram)
    text_generator = TextGenerator(bigram_weights)

    sql = 'SELECT * FROM PersonalDictionaries WHERE user_id = ?'
    values = [user_id]
    cursor = db.execute(sql, values)
    personal_words = []
    for row in cursor:
        personal_words.append(row['word'])
    text = text_generator.generate(personal_words, length)
    if len(text) > 0:
        sql = 'INSERT INTO Posts (post_id, user_id, text, type, time_stamp) VALUES (?,?,?,1,?) ' \
              'ON CONFLICT(post_id) DO UPDATE SET text = ?'
        values = [random.getrandbits(8), user_id, text, datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f'),
                  text]
        cursor = db.execute(sql, values)
        db.commit()
        return cursor.lastrowid
    else:
        return 0

