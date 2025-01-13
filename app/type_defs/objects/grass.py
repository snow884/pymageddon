import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.emit_object import EmitObject


class Grass(BaseObject):

    type_name: str = "Grass"

    image = "../../static/objects/grass.png"

    def __init__(
        self, x_new: int, y_new: int, code: str = None, code_store: str = None
    ):
        super().__init__(x_new, y_new, code=code, code_store=code_store)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    effects = [EmitObject(object_to_emit="Seed", time_to_emit=80)]

    rgb_map = (0, 204, 0)
