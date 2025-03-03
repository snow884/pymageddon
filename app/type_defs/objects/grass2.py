import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.emit_object import EmitObject


class Grass2(BaseObject):

    type_name: str = "Grass2"

    image = "../../static/objects/grass2.png"

    def __init__(
        self,
        x_new: int,
        y_new: int,
        code: str = None,
        code_store: str = None,
        family_name: str = None,
    ):
        super().__init__(
            x_new, y_new, code=code, code_store=code_store, family_name=family_name
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    effects = [EmitObject(object_to_emit="Seed2", time_to_emit=40)]

    rgb_map = (0, 204, 0)

    def get_description_short(self) -> str:

        return "Grass is a plant. Grass can produce seeds."
