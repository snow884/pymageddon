from type_defs.particles.base_particle import BaseParticle


class TrackParticle(BaseParticle):

    type_name: str = "Track"

    image: str = "../../static/particles/tracks.png"

    lifetime: int = 10

    motion: str = "ground_stuck"

    def __init__(self, x_new: int, y_new: int, rotation):

        super().__init__(x_new, y_new)

        self.rotation = rotation
