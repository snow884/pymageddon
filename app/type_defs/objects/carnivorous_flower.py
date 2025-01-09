import random

from common_utils.common_enums import Rotations
from type_defs.objects.base_object import BaseObject
from type_defs.objects.effects.eat_object_stepping_in import EatObjectSteppingIn
from type_defs.objects.effects.emit_object import EmitObject
from type_defs.objects.effects.hp_depletion import HpDepletion


class CarnivorousFlower(BaseObject):

    type_name: str = "CarnivorousFlower"

    image = "../../static/objects/carnivorous_flower.png"

    hp = 10

    def __init__(
        self, x_new: int, y_new: int, code: str = None, code_store: str = None
    ):
        super().__init__(x_new, y_new, code=code, code_store=code_store)
        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )

    effects = [
        EmitObject(object_to_emit="CarnivorousFlowerSeed", time_to_emit=101),
        EatObjectSteppingIn(
            types_eaten_to_hp_conv={"Cow": 100, "Chicken": 100, "Fox": 100}
        ),
        HpDepletion(hp_loss_per_cycle=1, skip_cycles=20),
    ]
