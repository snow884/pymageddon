from type_defs.objects.effects.base_effect import BaseEffect


class HpDepletion(BaseEffect):
    def __init__(self, hp_loss_per_cycle=1, skip_cycles=3):
        super().__init__()

        self.hp_loss_per_cycle = hp_loss_per_cycle
        self.skip_cycles = skip_cycles

    def description(self):

        return f"""
        Looses {self.hp_loss_per_cycle} every {self.skip_cycles} cycles.
        """

    def run_effect(self, parent_object):

        cycle_counter = parent_object.variables.get("hp_depletion_cycle_counter", 0)

        cycle_counter = cycle_counter + 1

        if cycle_counter >= self.skip_cycles:
            cycle_counter = 0

            parent_object.hp = parent_object.hp - 1

            if parent_object.hp <= 0:

                parent_object.die()

        parent_object.variables["hp_depletion_cycle_counter"] = cycle_counter
