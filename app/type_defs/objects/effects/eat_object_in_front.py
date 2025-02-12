from common_utils.common_enums import Actions
from common_utils.utils import obj_fut
from singleton import realm
from type_defs.objects.effects.base_effect import BaseEffect
from type_defs.particles.eating_particle import EatingParticle


class EatObjectInFront(BaseEffect):
    effect_name = "Can eat objects in front of it"

    def __init__(self, types_eaten_to_hp_conv, effect_name=effect_name):
        super().__init__()
        self.types_eaten_to_hp_conv = types_eaten_to_hp_conv
        self.effect_name = effect_name

    def description(self):

        type_to_hp_str = ""

        for obj_type, reward in self.types_eaten_to_hp_conv.items():

            type_to_hp_str = (
                type_to_hp_str + f"* {obj_type.type_name} - receives {reward} hp <br>"
            )

        return f"Can eat the types the following types:<br>" + type_to_hp_str

    def run_effect(self, parent_object):

        self.types_eaten_to_hp_conv = {
            obj_fut(t): r for t, r in self.types_eaten_to_hp_conv.items()
        }

        if parent_object.intent == Actions.MOVE_FORWARD:
            x_new, y_new = parent_object.get_next_coords()

            tile = realm.TILES.get((x_new, y_new))

            if tile:

                occupied_by_obj_index = tile.occupied_by
                if occupied_by_obj_index:
                    obj_on_location = realm.OBJECT_LIST[occupied_by_obj_index]

                    for obj_type, reward in self.types_eaten_to_hp_conv.items():
                        if isinstance(obj_on_location, obj_type):

                            EatingParticle(parent_object.x, parent_object.y)
                            obj_on_location.die()
                            parent_object.hp = min(parent_object.hp + reward, 100)
