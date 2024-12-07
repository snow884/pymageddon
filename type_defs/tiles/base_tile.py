from dataclasses import dataclass

from dataclasses_json import dataclass_json

from common_utils.common_enums import Rotations


@dataclass_json
@dataclass
class BaseTile:

    index: int = 0
    type_name: str = "Undefined"
    x: int = 0
    y: int = 0
    rotation: int = Rotations.UP
    image: str = ""
    occupied_by: int = None
    occupied_by_particles = None

    def __init__(self, x, y):

        super().__init__()

        self.x = x
        self.y = y

        self.occupied_by_particles = []
