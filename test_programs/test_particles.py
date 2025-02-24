from base_test import Test

import jazz
from jazz import Globals, Vec2, Color, Draw, Texture
from jazz.particles import ParticleEmitter, Particle


def blow_smoke(x: int) -> Texture:
    cloud = Texture(Globals.renderer, (32, 32), target=True)
    cloud.blend_mode = 1
    with Draw.canvas(cloud):
        Draw.fill_circle(
            Vec2(16, 16), 4 + int(12 * (255 - x) / 255), Color(x, x, x, x)
        )
    return cloud


class ParticleTest(Test):
    name = "Particle Test"

    def __init__(self) -> None:
        super().__init__()
        self.emitter: ParticleEmitter = None
        self.gravity: Vec2 = Vec2(0, -200)

    def on_load(self, _):
        super().on_load(_)

        def particle_update(p: Particle, d: float):
            p.vel = p.vel.lerp(self.gravity, 0.2 * d)
            p.img = int(p.life / 3 * 255)

        self.emitter = self.add_object(
            ParticleEmitter(
                True,
                rate=50,
                pos=(400, 400),
                particle_spawn=50,
                particle_update=particle_update,
                emission_angles=[(-45, 45)],
                particle_graphics=[blow_smoke(x) for x in range(256)],
            )
        )
        self.create_timer(15, self.stop, ())

    def update(self, delta):
        self.emitter.rotate(60 * delta)
