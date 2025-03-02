import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.turn_into_near_object import TurnIntoNearObject


class BeeEgg(BaseObject):
    type_name: str = "BeeEgg"
    image = "../../static/objects/bee_egg.png"

    effects = [
        TurnIntoNearObject(
            future_object_class="Bee",
            object_class_list_to_turn_when_earby=["Cow", "Chicken", "Fox", "Badger"],
        )
    ]

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

        return (
            "Honeycomb is an egg that will hatch into a bee when other animal comes"
            " close."
        )
