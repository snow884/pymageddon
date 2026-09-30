import random

from common_utils.common_enums import Rotations
from common_utils.ecosystem import BREED_HP_COST, BREED_MIN_HP, DIETS, predators_of
from common_utils.think_utils import simple_chase
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.eat_object_in_front import EatObjectInFront
from type_defs.objects.effects.hp_depletion import HpDepletion
from type_defs.objects.effects.lay_object import LayObject
from type_defs.particles.blood_mark_particle import BlookMarkParticle
from type_defs.particles.death_particle import DeathParticle
from type_defs.particles.track_particle import TrackParticle


class Badger(BaseObject):

    type_name: str = "Badger"
    image = "../../static/objects/badger.png"
    is_alive = True

    effects = [
        EatObjectInFront(types_eaten_to_hp_conv=DIETS["Badger"]),
        HpDepletion(hp_loss_per_cycle=1, skip_cycles=1),
        LayObject(
            object_to_lay="BadgerEgg",
            time_to_lay=50,
            min_hp=BREED_MIN_HP,
            hp_cost=BREED_HP_COST,
        ),
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
        family_name: str = None,
    ):
        super().__init__(
            x_new=x_new,
            y_new=y_new,
            is_player=is_player,
            player_name=player_name,
            code=code,
            code_store=code_store,
            family_name=family_name,
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def think(self):
        if not self.code:
            return simple_chase(
                self,
                chase_after=list(DIETS["Badger"]),
                chase_from=predators_of("Badger"),
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
        BlookMarkParticle(x_new=self.x, y_new=self.y)
        super().die()

    def get_description_short(self) -> str:

        return (
            "Animal representing a badger that moves, eats mushrooms, snails and"
            " tortoise eggs and lays eggs. A badger can be eaten by a fox or a wolf."
        )
