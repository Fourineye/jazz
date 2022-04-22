"""Module that holds The input wrappers"""

import pygame
from pygame import Vector2


class InputHandler:
    """Input Wrapper"""

    def __init__(self):
        self.mouse = Mouse()
        self.keyboard = Keyboard()
        self.user_events = []

    def update(self):
        """Called every frame to update user input."""
        self.user_events = []
        self.mouse.update()
        self.keyboard.update()

        for event in pygame.event.get(pygame.USEREVENT):
            self.user_events.append(event)

        for event in pygame.event.get():
            pass


class Mouse:
    """Wrapper for mouse inputs."""

    def __init__(self):
        self.just_pressed = [False] * 6
        self.pressed = [False] * 6
        self.just_released = [False] * 6
        self.pos = Vector2()
        self.rel = Vector2()

    def update(self):
        """Called every frame to update mouse inputs."""
        self.just_pressed = [False] * 6
        self.just_released = [False] * 6
        self.pressed = pygame.mouse.get_pressed()
        self.pos = Vector2(pygame.mouse.get_pos())
        self.rel = Vector2(pygame.mouse.get_rel())
        for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
            self.just_pressed[event.button] = True
        for event in pygame.event.get(pygame.MOUSEBUTTONUP):
            self.just_released[event.button] = True

    @property
    def x(self):
        """Returns the x component of pos."""
        return self.pos.x

    @property
    def y(self):
        """Returns the y component of pos."""
        return self.pos.y

    @property
    def dx(self):
        """Retruns the x compnent of rel."""
        return self.rel.x

    @property
    def dy(self):
        """Returns the y component of rel."""
        return self.rel.y


class Keyboard:
    """Wrapper for keyboard inputs."""

    def __init__(self):
        self.just_pressed = [False] * 200
        self.pressed = [False] * 200
        self.just_released = [False] * 200

    def update(self):
        """Called every frame to update keyboard inputs."""
        self.just_pressed = [False] * 200
        self.just_released = [False] * 200
        self.pressed = pygame.key.get_pressed()

        for event in pygame.event.get(pygame.KEYDOWN):
            self.just_pressed[event.key] = True
        for event in pygame.event.get(pygame.KEYUP):
            self.just_released[event.key] = True
