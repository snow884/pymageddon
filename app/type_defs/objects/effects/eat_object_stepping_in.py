from common_utils.utils import obj_fut
from singleton import realm
from type_defs.objects.effects.base_effect import BaseEffect
from type_defs.particles.eating_particle import EatingParticle


class EatObjectSteppingIn(BaseEffect):
    def __init__(self, types_eaten_to_hp_conv):
        super().__init__()
        self.types_eaten_to_hp_conv = types_eaten_to_hp_conv

    def description(self):

        type_to_hp_str = ""

        for obj_type, reward in self.types_eaten_to_hp_conv.items():

            type_to_hp_str = type_to_hp_str + f"* {obj_type} - receives {reward} hp \n"

        return (
            f"""
        Can eat the the following types that step in:
        """
            + type_to_hp_str
        )

    def run_effect(self, parent_object):

        self.types_eaten_to_hp_conv = {
            obj_fut(t): r for t, r in self.types_eaten_to_hp_conv.items()
        }

        tile_up = realm.TILES.get((parent_object.x, parent_object.y - 1))
        tile_right = realm.TILES.get((parent_object.x + 1, parent_object.y))
        tile_down = realm.TILES.get((parent_object.x, parent_object.y + 1))
        tile_left = realm.TILES.get((parent_object.x - 1, parent_object.y))

        for tile in [tile_up, tile_right, tile_down, tile_left]:

            if tile:

                occupied_by_obj_index = tile.occupied_by
                if occupied_by_obj_index:
                    obj_on_location = realm.OBJECT_LIST[occupied_by_obj_index]

                    for obj_type, reward in self.types_eaten_to_hp_conv.items():
                        if isinstance(obj_on_location, obj_type):

                            x_new, y_new = obj_on_location.get_next_coords()

                            if x_new == parent_object.x and y_new == parent_object.y:

                                EatingParticle(parent_object.x, parent_object.y)
                                obj_on_location.die()
                                parent_object.hp = min(parent_object.hp + reward, 100)
