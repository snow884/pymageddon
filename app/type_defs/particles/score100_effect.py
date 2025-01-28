from type_defs.particles.base_particle import BaseParticle


class Score100Particle(BaseParticle):

    type_name: str = "Score100Particle"

    image: str = "../../static/particles/score100_effect.png"

    lifetime: int = 4

    motion: str = "scale"
