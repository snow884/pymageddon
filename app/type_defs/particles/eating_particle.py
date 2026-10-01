from type_defs.particles.base_particle import BaseParticle


class EatingParticle(BaseParticle):

    type_name: str = "Eating"

    image: str = "../../static/particles/eating.png"

    lifetime: int = 3

    motion: str = "up"

    fx: str = "eat"
    fx_sheet: str = "../../static/particles/fx/eat_sheet.png"
    fx_frames: int = 16
