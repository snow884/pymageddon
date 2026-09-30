import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.turn_into import TurnInto


class CowEgg(BaseObject):
    type_name: str = "CowEgg"
    image = "../../static/objects/egg.png"

    effects = [TurnInto(future_object_class="Calf", time_to_turn=100)]

    rgb_map = (255, 255, 255)

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

    def get_description_short(self) -> str:

        return "An egg that will hatch into a calf."
