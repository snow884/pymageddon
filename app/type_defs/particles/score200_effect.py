from type_defs.particles.base_particle import BaseParticle


class Score200Particle(BaseParticle):

    type_name: str = "Score200Particle"

    image: str = "../../static/particles/score200_effect.png"

    lifetime: int = 4

    motion: str = "scale"

    fx: str = "score"
    fx_sheet: str = "../../static/particles/fx/score_sheet.png"
    fx_frames: int = 16
    fx_label: str = "200"
