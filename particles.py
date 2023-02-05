from random import randint

import pygame
from pygame import Vector2

from Jazz.objects import GameObject


class Particle:
    """Basic Particle class, intended to be extended."""

    def __init__(
        self,
        pos: Vector2,
        vel: Vector2,
        life: float,
        color=(255, 255, 255),
    ):
        self._pos = pos
        self._vel = vel
        self._acc = Vector2(0, 100)
        self._life = life
        self.color = color

    def draw(self, surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vector2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vector2()
        pygame.draw.circle(
            surface, self.color, self._pos + Vector2(offset), int(self._life * 5)
        )

    def process(self, delta: float):
        """
        Method called once per frame to handle game logic. Called before render.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        self._pos += self._vel * delta
        self._vel += self._acc * delta
        self._life -= delta
        if self._life <= 0:
            return True
        return False


class ParticleEmitter(GameObject):
    """An object that handles particles"""

    def __init__(
        self, pos: Vector2, name="ParticleEmitter", active=False, rate=1, **kwargs
    ):
        GameObject.__init__(self, pos, name, **kwargs)
        self._pos = Vector2(pos)
        self._particles = []
        self.active = active
        self.rate = rate

    def emit_particles(self, num: int):
        """
        Creates particles at the current position.

        Args:
            num (int): The number of particles to create.
        """
        for _ in range(num):
            self._particles.append(
                Particle(
                    Vector2(self._pos),
                    Vector2(randint(25, 100), 0).rotate(randint(0, 365)),
                    2,
                    self._color,
                )
            )

    def draw(self, surface, offset=None):
        """
        Called once per frame, draws all particles currently in the object.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vector2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        for particle in self._particles:
            particle.draw(surface, offset)

    def process(self, delta: float):
        """
        Called once per frame, updates all Particle objects currently in the object.

        Args:
            delta (float): Time in seconds since last frame.
        """
        if self.active:
            self.emit_particles(self.rate)
        for particle in self._particles[::-1]:
            if particle.process(delta):
                self._particles.remove(particle)

    @property
    def pos(self):
        """Returns _pos attribute."""
        return Vector2(self._pos)

    @pos.setter
    def pos(self, pos: Vector2):
        """Sets _pos attribute."""
        self._pos = Vector2(pos)
