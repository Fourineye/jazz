from base_test import Test

from jazz import Globals
from jazz.particles import ParticleEmitter


class ParticleTest(Test):
    name = "Particle Test"

    def __init__(self):
        super().__init__()
        self.emitter: ParticleEmitter = None

    def on_load(self, _):
        super().on_load(_)
        self.emitter = self.add_object(
            ParticleEmitter(
                True,
                rate=50,
                pos=(400, 400),
                particle_spawn=50,
                emission_angles=[(-45, 45)],
            )
        )
        self.create_timer(15, self.stop, ())

    def update(self, delta):
        self.emitter.rotate(60 * delta)
