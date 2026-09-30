import random

from common_utils import ecosystem
from common_utils.utils import obj_fut
from singleton import realm
from type_defs.objects.effects.base_effect import BaseEffect


class EmitObject(BaseEffect):
    effect_name = "Can emit object in a location next to it"

    def __init__(self, object_to_emit, time_to_emit, effect_name=effect_name):
        super().__init__()

        self.object_to_emit = object_to_emit
        self.time_to_emit = time_to_emit
        self.effect_name = effect_name

    def description(self):

        obj_name = getattr(self.object_to_emit, "type_name", str(self.object_to_emit))
        return f"""
        Emits {obj_name} every {self.time_to_emit} cycles.
        """

    def run_effect(self, parent_object):

        cycle_counter = parent_object.variables.get("emit_object_cycle_counter", 0)

        obj_object_to_emit = obj_fut(self.object_to_emit)

        cycle_counter = cycle_counter + 1

        if cycle_counter > self.time_to_emit:

            x_new = random.choice([-1, 0, 1]) + parent_object.x
            y_new = random.choice([-1, 0, 1]) + parent_object.y

            tile = realm.TILES.get((x_new, y_new))

            if tile and ecosystem.birth_allowed(obj_object_to_emit.type_name):
                if tile.occupied_by is None:
                    obj_object_to_emit(x_new=x_new, y_new=y_new)

            cycle_counter = 0

        parent_object.variables["emit_object_cycle_counter"] = cycle_counter
