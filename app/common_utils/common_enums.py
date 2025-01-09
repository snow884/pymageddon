import json
from enum import Enum


# Custom JSON encoder
class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return json.JSONEncoder.default(self, obj)


class Rotations(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


class Actions(Enum):

    ROTATE_UP = 1
    ROTATE_RIGHT = 2
    ROTATE_DOWN = 3
    ROTATE_LEFT = 4

    MOVE_FORWARD = 6
