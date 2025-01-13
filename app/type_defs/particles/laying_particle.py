from type_defs.particles.base_particle import BaseParticle


class LayingParticle(BaseParticle):

    type_name: str = "Laying"

    image: str = "../../static/particles/laying.png"

    lifetime: int = 3
