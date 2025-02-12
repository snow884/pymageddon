import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject


class Stone(BaseObject):
    type_name: str = "Stone"
    image = "../../static/objects/stone.png"

    rgb_map = (153, 153, 153)

    def __init__(self, x_new: int, y_new: int, family_name: str = None):
        super().__init__(x_new, y_new, family_name=family_name)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    def get_description_short(self) -> str:

        return "A stone is just passively siting in one place and acts as an obstacle."
