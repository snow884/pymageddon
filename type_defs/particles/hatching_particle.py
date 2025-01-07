from type_defs.particles.base_particle import BaseParticle


class HetchingParticle(BaseParticle):

    type_name: str = "Hatching"

    image: str = "../../static/particles/hetching.png"

    lifetime: int = 3
