from type_defs.particles.base_particle import BaseParticle


class LayingParticle(BaseParticle):

    type_name: str = "Laying"

    image: str = "../../static/particles/laying.png"

    lifetime: int = 3

    motion: str = "up"

    fx: str = "lay"
    fx_sheet: str = "../../static/particles/fx/lay_sheet.png"
    fx_frames: int = 16
