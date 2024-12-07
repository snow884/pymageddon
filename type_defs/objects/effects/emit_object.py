import random

from common_utils.utils import obj_fut
from singleton import realm
from type_defs.objects.effects.base_effect import BaseEffect


class EmitObject(BaseEffect):
    def __init__(self, object_to_emit, time_to_emit):

        self.object_to_emit = object_to_emit
        self.time_to_emit = time_to_emit
        self.cycle_counter = 0

    def description(self):

        return f"""
        Emits {self.object_to_emit} every {self.time_to_emit} cycles.
        """

    def run_effect(self, parent_object):

        obj_object_to_emit = obj_fut(self.object_to_emit)

        self.cycle_counter = self.cycle_counter + 1

        if self.cycle_counter > self.time_to_emit:

            x_new = random.choice([-1, 0, 1]) + parent_object.x
            y_new = random.choice([-1, 0, 1]) + parent_object.y

            tile = realm.TILES.get((x_new, y_new))

            if tile:
                if tile.occupied_by is None:
                    obj_object_to_emit(x_new=x_new, y_new=y_new)

            self.cycle_counter = 0
