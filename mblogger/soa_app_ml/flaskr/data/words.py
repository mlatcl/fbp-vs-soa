from .db import get_db

POST_START_WORD = "^"


# Identify bigrams in post and save them in db
def update_bigrams(post):
    db = get_db()
    text = post['text']
    words = text.split(" ")
    words = [word for word in words if word]
    for bigram in zip([POST_START_WORD, *words], words):
        sql = 'INSERT INTO Bigrams (first_word, second_word, weight) VALUES (?, ?, 1) ' \
              'ON CONFLICT(first_word, second_word) DO UPDATE SET weight = weight + 1'
        values = [bigram[0], bigram[1]]
        db.execute(sql, values)
        db.commit()


# Add words used in a post to the post author's dictionary
def update_personal_dictionary(post):
    db = get_db()
    user_id = post['author_id']
    text = post['text']
    words = text.split(' ')
    for word in words:
        sql = 'INSERT INTO PersonalDictionaries (user_id, word) VALUES (?, ?) ' \
              'ON CONFLICT(user_id, word) DO UPDATE SET word = ?'
        values = [user_id, word, word]
        db.execute(sql, values)
        db.commit()


