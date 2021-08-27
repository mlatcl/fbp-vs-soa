from .db import get_db
from datetime import datetime
import random
import itertools as it

POST_START_WORD = "^"
PERSONAL_WORDS_WEIGHT = 10.0


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
    sql = 'SELECT * FROM PersonalDictionaries WHERE user_id = ?'
    values = [user_id]
    cursor = db.execute(sql, values)
    personal_words = []
    for word in cursor:
        personal_words.append(word['word'])

    sql = 'SELECT first_word FROM Bigrams'
    cursor1 = db.execute(sql)
    bigrams_dict = {}
    bigram_weights_dict = {}
    for row1 in cursor1:
        first_word = row1['first_word']
        sql = 'SELECT second_word, weight FROM Bigrams WHERE first_word = ?'
        values = [first_word]
        cursor2 = db.execute(sql, values)
        words = []
        for row2 in cursor2:
            words.append(row2['second_word'])
            bigram_weights_dict[first_word,row2['second_word']] = row2['weight']
        bigrams_dict[first_word] = words

    if len(personal_words) > 0 or len(personal_words) == 0:
        text = " ".join(it.islice(_word_generator(personal_words,bigrams_dict,bigram_weights_dict), length))
        if len(text) > 0:
            sql = 'INSERT INTO Posts (post_id, user_id, text, type, time_stamp) VALUES (?,?,?,1,?) ' \
                'ON CONFLICT(post_id) DO UPDATE SET text = ?'
            values = [random.getrandbits(8), user_id, text, datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f'), text]
            cursor = db.execute(sql, values)
            db.commit()
            return cursor.lastrowid
        else:
            return 0
    else:
        return 0


# Word generator
def _word_generator(personal_words, bigrams_dict, bigram_weights_dict):
    current_word = POST_START_WORD
    while True:
        next_words = list(bigrams_dict.get(current_word, []))
        next_weights = [
            (PERSONAL_WORDS_WEIGHT if next_word in personal_words else 1.0)
            * bigram_weights_dict[current_word, next_word]
            for next_word in next_words
        ]
        if not next_words:
            return

        next_word = random.choices(next_words, weights=next_weights)[0]
        current_word = next_word
        yield current_word
