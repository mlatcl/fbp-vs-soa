from .db import get_db
from datetime import datetime, timedelta


# Insert a new ride request in the database
def insert_ride(ride):
    db = get_db()
    sql = 'INSERT INTO RideRequest (ride_id, user_id, from_lat, from_lon, to_lat, to_lon, last_lat, last_lon, '
    sql = sql + 'request_time, update_time, state) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '
    sql = sql + 'ON CONFLICT(ride_id) DO UPDATE SET user_id = ?, from_lat = ?, from_lon = ?, to_lat = ?, to_lon = ?, '
    sql = sql + 'last_lat = ?, last_lon = ?, request_time = ?, update_time = ?, state = ?'
    values = [ride['ride_id'], ride['user_id'], ride['from_location']['lat'], ride['from_location']['lon'],
              ride['to_location']['lat'], ride['to_location']['lon'], ride['from_location']['lat'],
              ride['from_location']['lon'], datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'),
              datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'), ride['state'],
              ride['user_id'], ride['from_location']['lat'], ride['from_location']['lon'],
              ride['to_location']['lat'], ride['to_location']['lon'], ride['from_location']['lat'],
              ride['from_location']['lon'], datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'),
              datetime.strptime(ride['request_time'], '%Y-%m-%d %H:%M:%S.%f'), ride['state']]
    cursor = db.execute(sql, values)
    db.commit()
    return cursor.lastrowid


# Get list of ride requests
def get_all_rides():
    res = []
    db = get_db()
    sql = 'SELECT * FROM RideRequest'
    cursor = db.execute(sql)
    for ride in cursor:
        from_location = {'lat': ride['from_lat'], 'lon': ride['from_lon']}
        to_location = {'lat': ride['to_lat'], 'lon': ride['to_lon']}
        last_location = {'lat': ride['last_lat'], 'lon': ride['last_lon']}
        r = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'driver_id': ride['driver_id'],
             'from_location': from_location, 'to_location': to_location, 'last_location': last_location,
             'request_time': ride['request_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'allocation_time': ride['allocation_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'update_time': ride['update_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'state': ride['state'], 'event_type': ride['event_type'], 'evaluated':ride['evaluated']}
        res.append(r)
    return res


# Get rides by state:
def get_rides_by_state(state):
    res = []
    db = get_db()
    sql = 'SELECT * FROM RideRequest WHERE state = ?'
    values = [state]
    cursor = db.execute(sql, values)
    for ride in cursor:
        from_location = {'lat': ride['from_lat'], 'lon': ride['from_lon']}
        to_location = {'lat': ride['to_lat'], 'lon': ride['to_lon']}
        last_location = {'lat': ride['last_lat'], 'lon': ride['last_lon']}
        r = {'ride_id': ride['ride_id'], 'user_id': ride['user_id'], 'driver_id': ride['driver_id'],
             'from_location': from_location, 'to_location': to_location, 'last_location': last_location,
             'request_time': ride['request_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'allocation_time': ride['allocation_time'],
             'update_time': ride['update_time'].strftime('%Y-%m-%d %H:%M:%S.%f'),
             'state': ride['state'], 'event_type': ride['event_type']}
        res.append(r)
    return res


# Update ride request status
def update_ride(ride_id, info):
    db = get_db()
    sql = ''
    values = []
    for key, value in info.items():
        sql = sql + ' ' + key + ' = ?,'
        values.append(value)
    sql = sql[:-1]
    sql = 'UPDATE RideRequest SET' + sql + ' WHERE ride_id = ?'
    values.append(ride_id)
    cursor = db.execute(sql, values)
    db.commit()
    if cursor.rowcount > 0:
        return ride_id
    else:
        return None


# Get ride wait times
def get_ride_wait_times():
    db = get_db()
    sql = 'SELECT * FROM RideRequest WHERE state = ? AND evaluated is NULL'
    values = ['ENROUTE']
    cursor = db.execute(sql, values)
    return cursor
