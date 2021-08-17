from .db import get_db
import json


# Registers a new author in the database
def registers_author(author):
    db = get_db()
    sql = 'INSERT INTO Authors (author_name) VALUES (?)'
    values = [author['author_name']]
    cursor = db.execute(sql, values)
    db.commit()
    if cursor.rowcount == 0:
        return cursor.rowcount
    else:
        return cursor.lastrowid


# Registers a new follow in the database
def follows_author(follow):
    db = get_db()
    sql = 'INSERT INTO Follows (active_author, passive_author) VALUES (?, ?)'
    values = [follow['active_author'], follow['passive_author']]
    cursor = db.execute(sql, values)
    db.commit()
    if cursor.rowcount == 0:
        return cursor.rowcount
    else:
        return follow['passive_author']

    
# Get list of follows for an author
def get_list_follows(author):
    res = []
    db = get_db()
    sql = 'SELECT a1.author_name active_author, a2.author_name passive_author FROM Authors as a1, Follows as f, Authors as a2 WHERE a1.author_id = f.active_author ' \
          'and a2.author_id = f.passive_author and f.active_author = ?'
    values = [author['author_id']]
    cursor = db.execute(sql, values)
    for follow in cursor:
        r = {'active_author': follow['active_author'], 'passive_author': follow['passive_author']}
        res.append(r)
    return res


# Get list of followers for an author
def get_list_followers(author):
    res = []
    db = get_db()
    sql = 'SELECT a1.author_name passive_author, a2.author_name active_author FROM Authors as a1, Follows as f, Authors as a2 WHERE a1.author_id = f.passive_author ' \
          'and a2.author_id = f.active_author and f.passive_author = ?'
    values = [author['author_id']]
    cursor = db.execute(sql, values)
    for follow in cursor:
        r = {'passive_author': follow['passive_author'], 'active_author': follow['active_author']}
        res.append(r)
    return res
