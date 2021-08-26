from .db import get_db

POST_START_WORD = "^"


# Registers a new follow in the database
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

    sql = 'SELECT first_word, second_word, weight FROM Bigrams'
    cursor = db.execute(sql)
    for bigram in cursor:
        print(bigram['first_word'] + '::' + bigram['second_word'] + '::' + str(bigram['weight']))


# Get list of followers for an author
def update_personal_directory(post):
    db = get_db()
    user_id = post['author_id']
    text = post['text']
    words = text.split(' ')
    for word in words:
        sql = 'INSERT INTO PersonalDictionaries (user_id, word) VALUES (?, ?) ON CONFLICT(user_id, word) ' \
              'DO UPDATE SET word = ?'
        values = [user_id, word, word]
        db.execute(sql, values)
        db.commit()

    sql = 'SELECT user_id, word FROM PersonalDictionaries'
    cursor = db.execute(sql)
    for word in cursor:
        print(word['user_id'] + '::' + word['word'])

