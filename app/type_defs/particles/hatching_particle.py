from type_defs.particles.base_particle import BaseParticle


class HetchingParticle(BaseParticle):

    type_name: str = "Hatching"

    image: str = "../../static/particles/hetching.png"

    lifetime: int = 3

    motion: str = "up"

    fx: str = "hatch"
    fx_sheet: str = "../../static/particles/fx/hatch_sheet.png"
    fx_frames: int = 16
