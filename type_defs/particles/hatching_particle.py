from type_defs.particles.base_particle import BaseParticle


class HetchingParticle(BaseParticle):

    type_name: str = "Eating"

    image: str = "static/particles/hetching.png"

    lifetime: int = 3
