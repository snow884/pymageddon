import random

from common_utils.common_enums import Rotations
from common_utils.think_utils import simple_chase
from type_defs.objects.base_object import BaseObject
from type_defs.objects.chicken_egg import ChickenEgg
from type_defs.objects.effects.eat_object_in_front import EatObjectInFront
from type_defs.objects.effects.hp_depletion import HpDepletion
from type_defs.objects.effects.lay_object import LayObject
from type_defs.objects.seed import Seed
from type_defs.particles.death_particle import DeathParticle


class Chicken(BaseObject):

    type_name: str = "Chicken"
    image = "static/objects/chicken.png"
    is_alive = True

    effects = [
        EatObjectInFront(types_eaten_to_hp_conv={Seed: 10}),
        HpDepletion(),
        LayObject(object_to_lay=ChickenEgg, time_to_lay=300),
    ]

    def __init__(self, x_new: int, y_new: int, is_player=False, player_name=None):
        super().__init__(
            x_new=x_new, y_new=y_new, is_player=is_player, player_name=player_name
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def think(self):

        return simple_chase(self, chase_after=["Seed"], chase_from="Fox")

    def die(self):
        DeathParticle(x_new=self.x, y_new=self.y)
        super().die()
