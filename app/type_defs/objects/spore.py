import random

from common_utils.common_enums import Rotations
from common_utils.think_utils import simple_chase
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.turn_into_near_object import TurnIntoNearObject


class Spore(BaseObject):
    type_name: str = "Spore"
    image = "../../static/objects/spore.png"
    hp = 20

    effects = [
        TurnIntoNearObject(
            future_object_class="Mushroom",
            object_class_list_to_turn_when_earby=["Grass", "Grass2", "Grass3"],
        )
    ]

    rgb_map = (255, 204, 0)

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

        return "A spore is a type of a seed that turns into a mushroom"

    def think(self):

        if random.randint(0, 5) <= 2:
            intent = None
            return intent

        if not self.code:

            return simple_chase(
                self,
                chase_after=["Grass", "Grass2", "Grass3", "CarnivorousFlower"],
                chase_from=[],
            )
