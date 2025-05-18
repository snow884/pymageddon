import random

from common_utils.common_enums import Actions, Rotations
from common_utils.grid_utils import find_nearest
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.eat_object_in_front import EatObjectInFront
from type_defs.objects.effects.lay_object import LayObject
from type_defs.particles.track_particle import TrackParticle


class Angel(BaseObject):

    type_name: str = "Angel"
    image = "../../static/objects/angel.png"
    is_alive = True

    effects = [
        LayObject(object_to_lay="CowEgg", time_to_lay=51),
        LayObject(object_to_lay="ChickenEgg", time_to_lay=52),
        LayObject(object_to_lay="FoxEgg", time_to_lay=53),
        LayObject(object_to_lay="Seed", time_to_lay=54),
        LayObject(object_to_lay="Seed2", time_to_lay=55),
        LayObject(object_to_lay="Seed3", time_to_lay=56),
        LayObject(object_to_lay="Spore", time_to_lay=57),
        LayObject(object_to_lay="Spore2", time_to_lay=58),
        LayObject(object_to_lay="BadgerEgg", time_to_lay=59),
        LayObject(object_to_lay="BeeEgg", time_to_lay=60),
        # LayObject(object_to_lay="CarnivorousFlowerSeed", time_to_lay=59),
        EatObjectInFront(
            types_eaten_to_hp_conv={
                "Grass": 0,
                "Grass2": 0,
                "Grass3": 0,
                "Seed": 0,
                "Seed2": 0,
                "Seed3": 0,
                "CowEgg": 0,
                "ChickenEgg": 0,
                "FoxEgg": 0,
                "BadgerEgg": 0,
                "Spore": 0,
                "Spore2": 0,
                "Mushroom": 0,
                "Mushroom2": 0,
                "CarnivorousFlowerSeed": 0,
                "CarnivorousFlower": 0,
                "BeeEgg": 0,
            }
        ),
    ]

    rgb_map = (51, 102, 255)

    def __init__(
        self,
        x_new: int,
        y_new: int,
        is_player=False,
        player_name=None,
        code: str = None,
        code_store: str = None,
    ):
        super().__init__(
            x_new=x_new,
            y_new=y_new,
            is_player=is_player,
            player_name=player_name,
            code=code,
            code_store=code_store,
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def think(self):

        chasing_num = self.variables.get("chasing_num", 0)

        random_num = self.variables.get("random_num", 0)
        chasing_dir = self.variables.get("chasing_dir", False)
        mode = self.variables.get("mode", "chase")

        last_x = self.variables.get("last_x", 0)
        last_y = self.variables.get("last_y", 0)

        stuck_num = self.variables.get("stuck_num", 0)

        intent = None

        if mode == "chase":

            if chasing_num == 0:

                chasing_dir = random.randint(0, 2) > 0

            chasing_num = chasing_num + 1

            if (last_x == self.x) or (last_y == self.y):
                stuck_num = stuck_num + 1

            if (chasing_num > 50) or (stuck_num > 5):
                stuck_num = 0
                chasing_num = 0
                mode = "random"

            found_obj = find_nearest(self, ["Fox", "Cow", "Chicken"])

            if found_obj:

                if chasing_dir:

                    if found_obj.x > self.x:
                        if self.rotation == Rotations.LEFT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_LEFT

                    if found_obj.x < self.x:
                        if self.rotation == Rotations.RIGHT:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_RIGHT

                    if found_obj.x == self.x:
                        chasing_dir = not (chasing_dir)

                else:

                    if found_obj.y > self.y:
                        if self.rotation == Rotations.UP:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_UP

                    if found_obj.y < self.y:
                        if self.rotation == Rotations.DOWN:
                            intent = Actions.MOVE_FORWARD
                        else:
                            intent = Actions.ROTATE_DOWN

                    if found_obj.y == self.y:
                        chasing_dir = not (chasing_dir)
            else:

                if random.randint(0, 5) >= 4:
                    intent = random.choice(list(Actions))
                else:
                    intent = Actions.MOVE_FORWARD

        if mode == "random":

            if random_num > 10:
                random_num = 0
                mode = "chase"

            random_num = random_num + 1

            if random.randint(0, 5) >= 4:
                intent = random.choice(list(Actions))
            else:
                intent = Actions.MOVE_FORWARD

        last_x = self.x
        last_y = self.y

        self.variables["last_x"] = last_x
        self.variables["last_y"] = last_y

        self.variables["stuck_num"] = stuck_num

        self.variables["chasing_num"] = chasing_num
        self.variables["random_num"] = random_num
        self.variables["chasing_dir"] = chasing_dir
        self.variables["mode"] = mode

        return intent

    def move_to_position(self, x_new: int, y_new: int):
        x_old = self.x
        y_old = self.y
        res = super().move_to_position(x_new, y_new)

        if res:
            TrackParticle(x_old, y_old, rotation=self.rotation)

        return res

    def get_description_short(self) -> str:

        return (
            "An angel acts as randomizer in the game. It has the ability to randomly"
            " lay eggs of all animal spices as well as seeds of all plants."
        )
