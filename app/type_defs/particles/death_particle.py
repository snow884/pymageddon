from type_defs.particles.base_particle import BaseParticle


class DeathParticle(BaseParticle):

    type_name: str = "Death"

    image: str = "../../static/particles/skull.png"

    lifetime: int = 3

    motion: str = "up"

    fx: str = "death"
    fx_sheet: str = "../../static/particles/fx/death_sheet.png"
    fx_frames: int = 16
