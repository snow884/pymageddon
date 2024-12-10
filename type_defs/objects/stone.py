import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject


class Stone(BaseObject):
    type_name: str = "Stone"
    image = "../../static/objects/stone.png"

    def __init__(self, x_new: int, y_new: int):
        super().__init__(x_new, y_new)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )
