from .db import get_db
import json


# Registers a new follow in the database
def follows_author(follow):
    db = get_db()
    sql = 'INSERT INTO Follows (active_author, passive_author, follow) VALUES (?, ?, ?) ' \
          'ON CONFLICT(active_author, passive_author) DO UPDATE SET follow = ?'
    values = [follow['active_author'], follow['passive_author'], follow['follow'], follow['follow']]
    cursor = db.execute(sql, values)
    db.commit()
    return cursor.lastrowid


# Get list of followers for an author
def get_list_followers():
    res = []
    db = get_db()
    sql = 'SELECT DISTINCT passive_author FROM Follows WHERE follow = 1'
    passive_authors = db.execute(sql)
    for passive_author in passive_authors:
        sql = 'SELECT active_author FROM Follows WHERE passive_author = ? AND follow = 1'
        values = [passive_author['passive_author']]
        active_authors = db.execute(sql,values)
        followers = []
        for active_author in active_authors:
            followers.append(active_author['active_author'])
        r = {'user_id' : passive_author['passive_author'], 'followers': followers}
        res.append(r)
    return res


# Get list of follows for an author
def get_list_followings():
    res = []
    db = get_db()
    sql = 'SELECT DISTINCT active_author FROM Follows WHERE follow = 1'
    active_authors = db.execute(sql)
    for active_author in active_authors:
        sql = 'SELECT passive_author FROM Follows WHERE active_author = ? AND follow = 1'
        values = [active_author['active_author']]
        passive_authors = db.execute(sql, values)
        followings = []
        for passive_author in passive_authors:
            followings.append(passive_author['passive_author'])
        r = {'user_id': active_author['active_author'], 'followings': followings}
        res.append(r)
    return res
