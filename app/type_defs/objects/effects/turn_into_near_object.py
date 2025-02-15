from common_utils.grid_utils import find_nearest
from common_utils.utils import obj_fut
from type_defs.objects.effects.base_effect import BaseEffect
from type_defs.particles.hatching_particle import HetchingParticle


class TurnIntoNearObject(BaseEffect):
    effect_name = "Will turn into a different object when nearby other objects"

    def __init__(
        self,
        future_object_class,
        object_class_list_to_turn_when_earby,
        effect_name=effect_name,
    ):
        super().__init__()

        self.object_class_to_turn_when_earby = object_class_list_to_turn_when_earby
        self.future_object_class = future_object_class
        self.effect_name = effect_name

    def description(self):

        str_near_obj_list = ",".join(self.object_class_to_turn_when_earby)

        return f"""
        When located near {str_near_obj_list} turns into {self.future_object_class.type_name}.
        """

    def run_effect(self, parent_object):

        self.future_object_class = obj_fut(self.future_object_class)

        obj_near_found = find_nearest(
            parent_object, self.object_class_to_turn_when_earby, rad=1
        )

        if obj_near_found:

            x_new = parent_object.x
            y_new = parent_object.y

            HetchingParticle(parent_object.x, parent_object.y)

            parent_object.die()
            self.future_object_class(
                x_new=x_new,
                y_new=y_new,
                code=parent_object.code_store,
                family_name=parent_object.family_name,
            )
