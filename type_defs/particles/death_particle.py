from type_defs.particles.base_particle import BaseParticle


class DeathParticle(BaseParticle):

    type_name: str = "Death"

    image: str = "static/particles/skull.png"

    lifetime: int = 3
