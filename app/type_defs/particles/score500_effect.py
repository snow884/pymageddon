from type_defs.particles.base_particle import BaseParticle


class Score500Particle(BaseParticle):

    type_name: str = "Score500Particle"

    image: str = "../../static/particles/score500_effect.png"

    lifetime: int = 4

    motion: str = "scale"
