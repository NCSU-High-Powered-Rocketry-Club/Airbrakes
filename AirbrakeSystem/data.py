# Library for very fast dataclass-like structs
# Technically has fast serialization/deserialization functionality too
# if we want to use it for logging
from msgspec import Struct


# Data point format class
class ABDataPoint(Struct):
    accel: float
    timestamp: int
    altitude: float
    velocity: float
