import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.turn_into import TurnInto


class CarnivorousFlowerSeed(BaseObject):
    type_name: str = "CarnivorousFlowerSeed"
    image = "../../static/objects/seed.png"

    effects = [TurnInto(future_object_class="CarnivorousFlower", time_to_turn=30)]

    rgb_map = (255, 204, 0)

    def __init__(
        self, x_new: int, y_new: int, code: str = None, code_store: str = None
    ):
        super().__init__(x_new, y_new, code=code, code_store=code_store)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def get_description_short(self) -> str:

        return "A seed of carnivorous flower"
