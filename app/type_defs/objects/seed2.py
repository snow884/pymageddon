import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.turn_into import TurnInto


class Seed2(BaseObject):
    type_name: str = "Seed2"
    image = "../../static/objects/seed2.png"

    effects = [TurnInto(future_object_class="Grass2", time_to_turn=30)]

    rgb_map = (255, 204, 0)

    def __init__(
        self, x_new: int, y_new: int, code: str = None, code_store: str = None
    ):
        super().__init__(x_new, y_new, code=code, code_store=code_store)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )
