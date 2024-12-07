from common_utils.utils import obj_fut
from type_defs.objects.effects.base_effect import BaseEffect


class TurnInto(BaseEffect):
    def __init__(self, future_object_class, time_to_turn):

        self.future_object_class = future_object_class
        self.time_to_turn = time_to_turn

        self.life_length = 0

    def description(self):

        return f"""
        After {self.time} cycles turns into {self.object_class}.
        """

    def run_effect(self, parent_object):

        self.future_object_class = obj_fut(self.future_object_class)

        self.life_length = self.life_length + 1

        if self.life_length > self.time_to_turn:
            x_new = parent_object.x
            y_new = parent_object.y

            parent_object.die()
            self.future_object_class(x_new=x_new, y_new=y_new)
