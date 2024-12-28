import json
from dataclasses import dataclass

from dataclasses_json import dataclass_json

from common_utils.common_enums import EnumEncoder
from singleton import realm


@dataclass
class Map:

    size_x: int = 0
    size_y: int = 0


class Score:
    type: str
    date: str
    value: int


@dataclass_json
@dataclass
class Player:
    name: str = ""


@dataclass_json
@dataclass
class Spectator:
    player_name: str = ""
    obj: object = None
    object_type: str = ""
    counter: int = 0
    lifetime: int = 0
    large_message: str = ""

    def __post_init__(self):

        realm.SPECTATOR_LIST[self.obj.index] = self

        print(self.obj.index)
        print(self.object_type)

    def effects(self):
        self.counter = self.counter + 1

        if self.counter >= self.lifetime:
            self.die()

    def die(self):
        del realm.SPECTATOR_LIST[self.obj.index]

        data = {
            "global_params": {
                "status": "game_over",
                "time_interval": realm.TIME_INTERVAL,
                "map_view_size": realm.MAP_VIEW_SIZE,
                "epoch": realm.EPOCH_COUNTER,
            },
            "player": {},
            "objects": {},
            "tiles": {},
            "particles": {},
        }

        realm.REDIS_CONNECTION.set(
            f"map_{self.player_name}", json.dumps(data, cls=EnumEncoder)
        )
