import random

from common_utils.common_enums import Rotations
from common_utils.think_utils import simple_chase
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.eat_object_in_front import EatObjectInFront
from type_defs.objects.effects.hp_depletion import HpDepletion
from type_defs.objects.effects.lay_object import LayObject
from type_defs.particles.death_particle import DeathParticle


class Cow(BaseObject):

    type_name: str = "Cow"
    image = "../../static/objects/cow.png"
    is_alive = True

    effects = [
        EatObjectInFront(
            types_eaten_to_hp_conv={
                "Seed": 10,
                "Grass": 20,
                "CarnivorousFlowerSeed": 10,
            }
        ),
        HpDepletion(hp_loss_per_cycle=1, skip_cycles=1),
        LayObject(object_to_lay="CowEgg", time_to_lay=50),
    ]

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
                chase_after=["Seed", "CarnivorousFlowerSeed", "Grass"],
                chase_from=["Fox"],
            )
        else:
            return super().think()

    def die(self):
        DeathParticle(x_new=self.x, y_new=self.y)
        super().die()
