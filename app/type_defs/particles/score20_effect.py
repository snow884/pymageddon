from type_defs.particles.base_particle import BaseParticle


class Score20Particle(BaseParticle):

    type_name: str = "Score20Particle"

    image: str = "../../static/particles/score20_effect.png"

    lifetime: int = 4

    motion: str = "scale"
