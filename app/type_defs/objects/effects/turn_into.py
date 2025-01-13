from common_utils.utils import obj_fut
from type_defs.objects.effects.base_effect import BaseEffect
from type_defs.particles.hatching_particle import HetchingParticle


class TurnInto(BaseEffect):
    def __init__(self, future_object_class, time_to_turn):
        super().__init__()

        self.future_object_class = future_object_class
        self.time_to_turn = time_to_turn

    def description(self):

        return f"""
        After {self.time_to_turn} cycles turns into {self.future_object_class}.
        """

    def run_effect(self, parent_object):

        cycle_counter = parent_object.variables.get("turn_into_cycle_counter", 0)

        self.future_object_class = obj_fut(self.future_object_class)

        cycle_counter = cycle_counter + 1

        if cycle_counter > self.time_to_turn:
            x_new = parent_object.x
            y_new = parent_object.y

            HetchingParticle(parent_object.x, parent_object.y)

            parent_object.die()
            self.future_object_class(
                x_new=x_new, y_new=y_new, code=parent_object.code_store
            )

        parent_object.variables["turn_into_cycle_counter"] = cycle_counter
