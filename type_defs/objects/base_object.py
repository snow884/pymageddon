from dataclasses import dataclass

from dataclasses_json import dataclass_json

from common_utils.common_enums import Actions, Rotations
from singleton import realm


@dataclass_json
@dataclass
class BaseObject:

    index: int = 0
    type_name: str = "Undefined"
    hp: int = 50
    is_alive: bool = False

    is_player: bool = False

    is_particle: bool = False

    player_name: str = ""

    image: str = ""
    intent: Actions = None

    x: int = 0
    y: int = 0
    rotation: int = Rotations.UP

    variables: object = None

    effects: object = None

    def __init__(self, x_new: int, y_new: int, is_player=False, player_name=None):

        super().__init__()

        self.variables = {}

        self.index = realm.OBJ_COUNTER
        realm.OBJ_COUNTER = realm.OBJ_COUNTER + 1

        if realm.TILES[(x_new, y_new)].occupied_by is not None:
            raise Exception(
                f"The position [{x_new},{y_new}] is already occupied by"
                f" {realm.OBJECT_LIST[realm.TILES[(x_new,y_new)].occupied_by]}"
            )

        realm.OBJECT_LIST[self.index] = self
        realm.TILES[(x_new, y_new)].occupied_by = self.index

        if is_player:
            self.player_name = player_name
            realm.PLAYER_LIST[self.player_name] = self

        self.x = x_new
        self.y = y_new
        self.is_player = is_player

    def __str__(self) -> str:

        return self.type_name + f" (ID {self.index})"

    def move_to_position(self, x_new: int, y_new: int) -> bool:

        if x_new >= realm.MAP.size_x or x_new < 0:
            # print(f"The position [{x_new},{y_new}] is outside of the realm.MAP size {realm.MAP.size_x }x{realm.MAP.size_y}")
            return False

        if y_new >= realm.MAP.size_y or y_new < 0:
            # print(f"The position [{x_new},{y_new}] is outside of the realm.MAP size {realm.MAP.size_x }x{realm.MAP.size_y}")
            return False

        if realm.TILES[(x_new, y_new)].occupied_by is not None:
            # print(f"The position [{x_new},{y_new}] is already occupied by {realm.OBJECT_LIST[realm.TILES[(x_new,y_new)].occupied_by]}")
            return False

        realm.TILES[(self.x, self.y)].occupied_by = None
        realm.TILES[(x_new, y_new)].occupied_by = self.index

        self.x = x_new
        self.y = y_new

        return True

    def get_next_coords(self, direction=1):

        if not self.intent == Actions.MOVE_FORWARD:
            return self.x, self.y
        else:

            x_new = self.x
            y_new = self.y

            if self.rotation == Rotations.UP:

                y_new = self.y - 1 * direction

            elif self.rotation == Rotations.RIGHT:

                x_new = self.x + 1 * direction

            elif self.rotation == Rotations.DOWN:

                y_new = self.y + 1 * direction

            elif self.rotation == Rotations.LEFT:

                x_new = self.x - 1 * direction

            return x_new, y_new

    def think(self):
        pass

    def run_effects(self):
        for e in self.effects:
            e.run_effect()

    def die(self):
        realm.TILES[(self.x, self.y)].occupied_by = None
        del realm.OBJECT_LIST[self.index]

        if self.is_player:
            print(f"Player {self.player_name} died")
            del realm.PLAYER_LIST[self.player_name]
