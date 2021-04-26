from .db import get_db
from datetime import datetime


# Insert a new ride request in the database
def insert_ride(ride):
    db = get_db()
    cursor = db.execute(
        'INSERT INTO RideRequest (ride_id, user_id, from_lat, from_lon, to_lat, to_lon, request_time) VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT(ride_id) DO UPDATE SET user_id = ?, from_lat = ?, from_lon = ?, to_lat = ?, to_lon = ?, request_time = ?',
        (ride['ride_id'], ride['user_id'], ride['from_lat'], ride['from_lon'], ride['to_lat'], ride['to_lon'],
         datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'), ride['user_id'], ride['from_lat'],
         ride['from_lon'], ride['to_lat'], ride['to_lon'],
         datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'))
    )
    db.commit()
    return cursor.lastrowid


# Insert a list of rides in the database
def insert_rides(rides):
    affected = 0
    for ride in rides:
        affected = insert_ride(ride)
    return affected


# Get list of ride requests
def get_all_rides():
    res = []
    db = get_db()
    cursor = db.execute('SELECT * FROM RideRequest')
    for ride in cursor:
        r = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'from_lat': ride['from_lat'],
             'from_lon': ride['from_lon'], 'to_lat': ride['to_lat'],
             'to_lon': ride['to_lon'], 'request_time': ride['request_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'allocation_time': ride['allocation_time'], 'state': ride['state'], 'event_type': ride['event_type'],
             'event_data': ride['event_data']}
        res.append(r)
    return res


# Get a ride by id
def get_ride(ride_id):
    res = {}
    db = get_db()
    cursor = db.execute(
        'SELECT * FROM RideRequest WHERE ride_id = ?',
        (ride_id,)
    )
    for ride in cursor:
        res = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'from_lat': ride['from_lat'],
               'from_lon': ride['from_lon'], 'to_lat': ride['to_lat'],
               'to_lon': ride['to_lon'], 'request_time': ride['request_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
               'allocation_time': ride['allocation_time'], 'state': ride['state'], 'event_type': ride['event_type'],
               'event_data': ride['event_data']}
    if res == {}:
        return None
    else:
        return res


# Update ride request status
def update_ride(ride_id, state):
    db = get_db()
    cursor = db.execute(
        'UPDATE RideRequest SET state = ?, allocation_time = ? WHERE ride_id = ?',
        (state, datetime.now(), ride_id)
    )
    db.commit()
    if cursor.rowcount > 0:
        return ride_id
    else:
        return None


# Remove all ride requests
def remove_all_rides():
    db = get_db()
    db.execute('DELETE FROM RideRequest')
    db.commit()
