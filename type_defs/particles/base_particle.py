from dataclasses import dataclass

from dataclasses_json import dataclass_json

from common_utils.common_enums import Rotations
from singleton import realm


@dataclass_json
@dataclass
class BaseParticle:
    x: int = 0
    y: int = 0
    rotation: int = Rotations.UP

    is_particle: bool = True
    is_alive: bool = False

    index: int = 0

    type_name: str = "Undefined"

    image: str = ""

    lifetime: int = 3
    life: int = 0

    def __init__(self, x_new: int, y_new: int):

        super().__init__()

        self.index = realm.OBJ_COUNTER
        realm.OBJ_COUNTER = realm.OBJ_COUNTER + 1

        realm.PARTICLE_LIST[self.index] = self
        realm.TILES[(x_new, y_new)].occupied_by_particles.append(self.index)

        self.x = x_new
        self.y = y_new

    def effects(self):
        self.life = self.life + 1
        if self.life >= self.lifetime:
            self.die()

    def die(self):
        realm.TILES[(self.x, self.y)].occupied_by_particles = list(
            set(realm.TILES[(self.x, self.y)].occupied_by_particles) - set([self.index])
        )
        del realm.PARTICLE_LIST[self.index]
