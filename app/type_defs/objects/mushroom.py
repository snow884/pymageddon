import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.emit_object import EmitObject


class Mushroom(BaseObject):

    type_name: str = "Mushroom"

    image = "../../static/objects/mushroom.png"

    def __init__(
        self,
        x_new: int,
        y_new: int,
        code: str = None,
        code_store: str = None,
        family_name: str = None,
        variables={},
    ):
        super().__init__(
            x_new,
            y_new,
            code=code,
            code_store=code_store,
            family_name=family_name,
            variables=variables,
        )
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    effects = [EmitObject(object_to_emit="Spore", time_to_emit=80 * 3)]

    rgb_map = (255, 153, 255)

    def get_description_short(self) -> str:

        return (
            "Mushroom is a type of edible fungus similar to plants. Mushroom can"
            " produce spores and that is how they spread."
        )
