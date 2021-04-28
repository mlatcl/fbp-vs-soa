DROP TABLE IF EXISTS RideRequest;

CREATE TABLE RideRequest(
  ride_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  driver_id INTEGER,
  from_lat FLOAT NOT NULL,
  from_lon FLOAT NOT NULL,
  to_lat FLOAT NOT NULL,
  to_lon FLOAT NOT NULL,
  last_lat FLOAT NOT NULL,
  last_lon FLOAT NOT NULL,
  request_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  allocation_time TIMESTAMP,
  update_time TIMESTAMP,
  state TEXT NOT NULL,
  event_type TEXT
);

