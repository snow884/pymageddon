import random

from common_utils.common_enums import Rotations
from common_utils.think_utils import simple_chase
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.eat_object_in_front import EatObjectInFront
from type_defs.objects.effects.hp_depletion import HpDepletion
from type_defs.objects.effects.lay_object import LayObject
from type_defs.particles.death_particle import DeathParticle
from type_defs.particles.track_particle import TrackParticle


class Cow(BaseObject):

    type_name: str = "Cow"
    image = "../../static/objects/cow.png"
    is_alive = True

    effects = [
        EatObjectInFront(
            types_eaten_to_hp_conv={
                "Seed": 10,
                "Seed2": 10,
                "Seed3": 10,
                "Grass": 20,
                "Grass2": 20,
                "Grass3": 20,
                "CarnivorousFlowerSeed": 10,
            }
        ),
        HpDepletion(hp_loss_per_cycle=1, skip_cycles=1),
        LayObject(object_to_lay="CowEgg", time_to_lay=50),
    ]

    rgb_map = (0, 0, 0)

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
        if not self.code:
            return simple_chase(
                self,
                chase_after=[
                    "Seed",
                    "Seed2",
                    "Seed3",
                    "CarnivorousFlowerSeed",
                    "Grass",
                    "Grass2",
                    "Grass3",
                ],
                chase_from=["Fox", "CarnivorousFlower"],
            )
        else:
            return super().think()

    def move_to_position(self, x_new: int, y_new: int):
        x_old = self.x
        y_old = self.y
        res = super().move_to_position(x_new, y_new)

        if res:
            TrackParticle(x_old, y_old, rotation=self.rotation)

        return res

    def die(self):
        DeathParticle(x_new=self.x, y_new=self.y)
        super().die()
