from dataclasses import dataclass
from random import choice, randint, uniform

import pygame
from pygame._sdl2 import Texture, Image

from .engine.base_object import GameObject
from .global_dict import Globals
from .utils import Vec2, Rect


@dataclass
class Particle:
    pos: Vec2
    vel: Vec2
    img: int
    life: float
    rot: float = 0


class ParticleEmitter(GameObject):
    """An object that handles particles"""

    def __init__(self, active=False, rate=1, **kwargs):
        kwargs.setdefault("name", "Particle Emitter")
        super().__init__(**kwargs)
        self._particles: list[Particle] = []
        self._particle_graphics = kwargs.get("particle_graphics", None)
        self._particle_spawn = kwargs.get("particle_spawn", None)
        self._particle_life = kwargs.get("particle_life", 2)
        self._particle_update = kwargs.get("particle_update", None)
        self._emission_angles = kwargs.get("emission_angles", [(0, 360)])
        self._emission_speed = kwargs.get("emission_speed", [(10, 100)])
        self.active = active
        self.rate = rate
        self._emission = 0
        if self._particle_graphics is None:
            self._particle_graphics = ["default"]

    def on_load(self):
        if Globals.app.experimental:
            for i, graphic in enumerate(self._particle_graphics):
                if not isinstance(graphic, (Texture, Image)):
                    self._particle_graphics[i] = Globals.scene.load_resource(
                        graphic, Globals.scene.TEXTURE
                    )
        else:
            for i, graphic in enumerate(self._particle_graphics):
                if not isinstance(graphic, pygame.Surface):
                    self._particle_graphics[i] = Globals.scene.load_resource(graphic)
        Globals.scene.add_sprite(self)

    def emit_particles(self, num: int):
        """
        Creates particles at the current position.

        Args:
            num (int): The number of particles to create.
        """
        for _ in range(num):
            self.add_particle()

    def add_particle(self):
        spawn_offset = Vec2()
        if self._particle_spawn is not None:
            if isinstance(self._particle_spawn, pygame.Rect):
                spawn_offset.update(
                    uniform(self._particle_spawn.left, self._particle_spawn.right),
                    uniform(self._particle_spawn.top, self._particle_spawn.bottom),
                )
                vel = Vec2(uniform(*choice(self._emission_speed)), 0).rotate(
                    uniform(*choice(self._emission_angles))
                )
            if isinstance(self._particle_spawn, (int, float)):
                spawn_offset.update(uniform(0, self._particle_spawn), 0)
                spawn_offset.rotate_ip(uniform(*choice(self._emission_angles)))
                vel = spawn_offset.normalize() * uniform(*choice(self._emission_speed))
        particle = Particle(
            self.pos + spawn_offset,
            vel,
            randint(0, len(self._particle_graphics) - 1),
            self._particle_life,
        )
        self._particles.append(particle)

    def draw(self, surface, offset=None):
        """
        Called once per frame, draws all particles currently in the object.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vector2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vec2()
        blits = []
        for particle in self._particles:
            blits.append(
                (
                    particle.img,
                    particle.pos + offset - Vec2(particle.img.get_size()) / 2,
                )
            )
        surface.fblits(blits)

    def render(self, offset):
        for particle in self._particles:
            img = self._particle_graphics[particle.img]
            dest = Rect(
                particle.pos + offset - Vec2(img.get_rect().size) / 2,
                img.get_rect().size,
            )
            self._particle_graphics[particle.img].draw(
                None,
                dest,
                particle.rot,
            )

    def update(self, delta: float):
        """
        Called once per frame, updates all Particle objects currently in the object.

        Args:
            delta (float): Time in seconds since last frame.
        """
        if self.active:
            self._emission += self.rate * delta
            if self._emission > 1:
                self.emit_particles(int(self._emission))
                self._emission %= 1
        for particle in self._particles[::-1]:
            particle.pos += particle.vel * delta
            particle.life -= delta
            if callable(self._particle_update):
                self._particle_update(particle, delta)
            if particle.life < 0:
                self._particles.remove(particle)

    def activate(self):
        self._emission = 0
        self.active = True

    def deactivate(self):
        self.active = False
