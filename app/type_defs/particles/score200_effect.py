from type_defs.particles.base_particle import BaseParticle


class Score200Particle(BaseParticle):

    type_name: str = "Score200Particle"

    image: str = "../../static/particles/score200_effect.png"

    lifetime: int = 4

    motion: str = "scale"
