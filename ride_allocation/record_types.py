from dataclasses import dataclass
from dataclasses_json import dataclass_json
from datetime import datetime
from enum import Enum
from typing import Dict


# if we need equality, consider these two threads
# https://stackoverflow.com/questions/34570814/equality-overloading-for-namedtuple
# https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes


class Record:
    @property
    def record_id(self):
        return id(self)


@dataclass_json
@dataclass
class Location(Record):
    lat: float
    lon: float


@dataclass_json
@dataclass
class RideRequest(Record):
    ride_id: int
    user_id: int
    request_time: datetime
    from_location: Location
    to_location: Location


class RideEventType(Enum):
    START = "START"
    COMPLETE = "COMPLETE"
    CANCEL = "CANCEL"
    LOCATION = "LOCATION"


@dataclass_json
@dataclass
class RideEvent(Record):
    ride_id: int
    event_time: datetime
    event_type: RideEventType
    event_data: Dict


class RideStatus(Enum):
    UNASSIGNED = "UNASSIGNED"
    DRIVER_ASSIGNED = "DRIVER_ASSIGNED"
    ENROUTE = "ENROUTE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


@dataclass_json
@dataclass
class RideInformation(Record):
    ride_id: int
    user_id: int
    driver_id: int
    ride_status: RideStatus
    update_time: datetime
    last_location: Location


@dataclass_json
@dataclass
class RideWaitInfo(Record):
    ride_id: int
    request_time: datetime
    wait_duration: float
    location: Location


class DriverState(Enum):
    AVAILABLE = "AVAILABLE"
    ASSIGNED = "ASSIGNED"
    OFFLINE = "OFFLINE"


@dataclass_json
@dataclass
class DriverStatus(Record):
    driver_id: int
    update_time: datetime
    state: DriverState

@dataclass_json
@dataclass
class DriverLocation(Record):
    driver_id: int
    location_time: datetime
    location: Location


@dataclass
class DriverInformation(Record):
    driver_id: int
    last_state: DriverState
    last_location: Location
    update_time: datetime


@dataclass_json
@dataclass
class EstimatedRideWaitInfo(Record):
    ride_id: int
    wait_time: float