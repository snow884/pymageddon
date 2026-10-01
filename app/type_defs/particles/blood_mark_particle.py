import random

from common_utils.common_enums import Rotations
from type_defs.particles.base_particle import BaseParticle


class BlookMarkParticle(BaseParticle):

    type_name: str = "BlookMark"

    image: str = "../../static/particles/blood_mark.png"

    lifetime: int = 20

    motion: str = "ground_stuck"

    fx: str = "blood"

    def __init__(self, x_new: int, y_new: int):

        super().__init__(x_new, y_new)

        self.rotation = random.choice(
            [Rotations.DOWN, Rotations.UP, Rotations.LEFT, Rotations.RIGHT]
        )
