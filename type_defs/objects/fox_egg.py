import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.turn_into import TurnInto


class FoxEgg(BaseObject):
    type_name: str = "FoxEgg"
    image = "../../static/objects/egg.png"

    effects = [TurnInto(future_object_class="Fox", time_to_turn=100)]

    def __init__(
        self, x_new: int, y_new: int, code: str = None, code_store: str = None
    ):
        super().__init__(x_new, y_new, code=code, code_store=code_store)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )
