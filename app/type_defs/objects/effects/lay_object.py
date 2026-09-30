import random

from common_utils.utils import obj_fut
from singleton import realm
from type_defs.objects.effects.base_effect import BaseEffect
from type_defs.particles.laying_particle import LayingParticle


class LayObject(BaseEffect):
    effect_name = "Can lay object behind it"

    def __init__(self, object_to_lay, time_to_lay, effect_name=effect_name):
        super().__init__()

        self.object_to_lay = object_to_lay
        self.time_to_lay = time_to_lay
        self.effect_name = effect_name

    def description(self):

        lay_name = getattr(self.object_to_lay, "type_name", str(self.object_to_lay))
        return f"""
        Every {self.time_to_lay} cycles lays a {lay_name}.
        """

    def run_effect(self, parent_object):

        self.object_to_lay = obj_fut(self.object_to_lay)

        cycle_counter = parent_object.variables.get(
            "lay_object_cycle_counter_" + self.object_to_lay.type_name, 0
        )

        code = parent_object.code
        family_name = parent_object.family_name

        cycle_counter = cycle_counter + 1

        if cycle_counter > self.time_to_lay:

            x_new, y_new = parent_object.get_next_coords(-1)
            tile = realm.TILES.get((x_new, y_new))
            if tile:
                if tile.occupied_by is None:

                    if (
                        parent_object.type_name == "Angel"
                        and self.object_to_lay.type_name == "CowEgg"
                    ):

                        code_family_list = []

                        for family_name_i, family_obj in realm.SCORE_LIST[
                            "players"
                        ].items():

                            for code_sha1, score_obj in family_obj[
                                "family_scores"
                            ].items():
                                if score_obj["code"]:
                                    code_family_list.append(
                                        {
                                            "code": score_obj["code"],
                                            "sha1": code_sha1,
                                            "family_name": family_name_i,
                                        }
                                    )

                        if len(code_family_list) == 0:
                            code = None
                            family_name = None
                        else:

                            sel_code_family = random.choice(code_family_list)

                            code = sel_code_family["code"]
                            family_name = sel_code_family["family_name"]

                            print("code")
                            print(code)
                            print("family_name")
                            print(family_name)

                    LayingParticle(parent_object.x, parent_object.y)
                    self.object_to_lay(
                        x_new=x_new,
                        y_new=y_new,
                        code_store=code,
                        family_name=family_name,
                    )
                    cycle_counter = 0

        parent_object.variables[
            "lay_object_cycle_counter_" + self.object_to_lay.type_name
        ] = cycle_counter
