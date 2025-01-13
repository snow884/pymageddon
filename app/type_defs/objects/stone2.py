import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject


class Stone2(BaseObject):
    type_name: str = "Stone2"
    image = "../../static/objects/stone2.png"

    rgb_map = (153, 153, 153)

    def __init__(self, x_new: int, y_new: int):
        super().__init__(x_new, y_new)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )
