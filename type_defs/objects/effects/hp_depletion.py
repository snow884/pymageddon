from type_defs.objects.effects.base_effect import BaseEffect


class HpDepletion(BaseEffect):
    def __init__(self, hp_loss_per_cycle=1, skip_cycles=3):

        self.hp_loss_per_cycle = hp_loss_per_cycle
        self.skip_cycles = skip_cycles
        self.cycle_counter = 0

    def description(self):

        return f"""
        Looses {self.hp_loss_per_cycle} every {self.skip_cycles} cycles.
        """

    def run_effect(self, parent_object):

        self.cycle_counter = self.cycle_counter + 1

        if self.cycle_counter >= 3:
            self.cycle_counter = 0

            parent_object.hp = parent_object.hp - 1

            if parent_object.hp <= 0:

                parent_object.die()
