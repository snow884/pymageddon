from common_utils.utils import obj_fut
from singleton import realm
from type_defs.objects.effects.base_effect import BaseEffect


class LayObject(BaseEffect):
    def __init__(self, object_to_lay, time_to_lay):
        super().__init__()

        self.object_to_lay = object_to_lay
        self.time_to_lay = time_to_lay

    def description(self):

        return f"""
        Every {self.time_to_lay} cycles lays a {self.object_to_lay}.
        """

    def run_effect(self, parent_object):

        self.object_to_lay = obj_fut(self.object_to_lay)

        cycle_counter = parent_object.variables.get(
            "lay_object_cycle_counter_" + self.object_to_lay.type_name, 0
        )

        cycle_counter = cycle_counter + 1

        if cycle_counter > self.time_to_lay:

            x_new, y_new = parent_object.get_next_coords(-1)
            tile = realm.TILES.get((x_new, y_new))
            if tile:
                if tile.occupied_by is None:
                    self.object_to_lay(x_new=x_new, y_new=y_new)
                    cycle_counter = 0

        parent_object.variables[
            "lay_object_cycle_counter_" + self.object_to_lay.type_name
        ] = cycle_counter
