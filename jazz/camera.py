from typing import Type, TYPE_CHECKING

from random import randint

import pygame

from .global_dict import Globals
from .utils import (
    Rect,
    Vec2,
    Color,
    clamp,
    FOLLOW_STRICT,
    FOLLOW_SMOOTH,
    JazzException,
)

if TYPE_CHECKING:
    from .engine import GameObject


class Camera:
    """Class that handles the drawing of objects onto the display."""

    def __init__(self):
        self._bg_color = (0, 0, 0)
        self._blanking = True
        self.target = None
        self.bounds = None
        self.follow_type = FOLLOW_STRICT
        self.offset = Vec2()
        self.shake = Vec2()
        self.magnitude = 0
        self.damping = 0.1
        self.display_center = (
            Globals.display.get_width() / 2,
            Globals.display.get_height() / 2,
        )
        self.zoom = 1

    def update(self, _delta: float) -> None:
        """
        Called every frame to update the offset and shake values

        Args:
            _delta (float): For Engine compatibility. Unused.
        """
        if self.target:
            self.update_offset()
        if self.magnitude > 0.1:
            self.magnitude -= self.magnitude * self.damping
            self.shake = Vec2(
                self.magnitude * randint(-10, 10),
                self.magnitude * randint(-10, 10),
            )
        else:
            self.shake = Vec2()
            self.magnitude = 0

    def render(self) -> None:
        """Renders visible objects to the screen."""
        draw_objects = Globals.scene.sprites

        if self._blanking:
            Globals.renderer.draw_color = self._bg_color
            Globals.renderer.clear()

        for obj in draw_objects:
            if obj.visible:
                if obj.screen_space:
                    obj.render(Vec2())
                else:
                    obj.render(self.offset + self.shake)

    def render_debug(self) -> None:
        """Renders debug information about visible objects."""
        draw_objects = Globals.scene.objects

        for obj in draw_objects:
            if getattr(obj, "visible", False):
                if obj.screen_space:
                    obj._render_debug(Vec2())
                else:
                    obj._render_debug(self.offset + self.shake)

    def update_offset(self) -> None:
        """Updates the Camera offset to the target."""
        if self.target is None:
            return
        offset_x, offset_y = self.offset
        if isinstance(self.target, Vec2):
            target_x = self.target.x
            target_y = self.target.y
        else:
            target_x, target_y = self.target.pos

        if self.follow_type == FOLLOW_STRICT:
            offset_x = self.display_center[0] - target_x
            offset_y = self.display_center[1] - target_y
        elif self.follow_type == FOLLOW_SMOOTH:
            offset_x += (self.display_center[0] - target_x - offset_x) / 5
            offset_y += (self.display_center[1] - target_y - offset_y) / 5

        if self.bounds is not None:
            offset_x = clamp(
                offset_x,
                -self.bounds.right + Globals.display.get_width(),
                -self.bounds.left,
            )
            offset_y = clamp(
                offset_y,
                -self.bounds.bottom + Globals.display.get_height(),
                -self.bounds.top,
            )

        self.offset.update(offset_x, offset_y)

    def set_offset(self, position=(0, 0)) -> None:
        """Sets the camera offset to a specified value

        Args:
            position (tuple, optional): New offset to set the Camera to.
                Defaults to (0, 0).
        """
        offset_x = self.display_center[0] - position[0]
        offset_y = self.display_center[1] - position[1]
        self.offset.update(offset_x, offset_y)

    def set_target(self, target: Type["GameObject"]) -> None:
        """
        Sets the target of the Camera, which it will follow.

        Args:
            target (GameObject, Vec2): The target to follow.
        """
        if isinstance(target, object):
            self.target = target
        else:
            raise JazzException("Camera can only be set to follow an object")

    def set_bounds(self, bounds: Rect | tuple[int, int, int, int]) -> None:
        """This method sets the world coordinantes bounds of the camera.

        Args:
            bounds (Rect | tuple[int, int, int, int]): The Rectangle that the
                camera will stay inside of.
        """
        if len(bounds) != 4:
            raise JazzException(
                "Bounds must be pygame rect or a iterable with length 4"
            )
        if isinstance(bounds, pygame.Rect):
            self.bounds = bounds
        else:
            self.bounds = Rect(*bounds)

    def set_bg_color(self, color: Color | tuple[int, int, int] | str) -> None:
        self._bg_color = Color(color)

    def add_shake(self, magnitude) -> None:
        """
        Adds magnitude to the Camera shake.

        Args:
            magnitude (float): The magnitude of the shake to add.
        """
        self.magnitude = magnitude
        self.shake = Vec2()

    @property
    def pos(self) -> Vec2:
        return self.display_center - self.offset

    @property
    def screen_rect(self) -> Rect:
        return Rect(
            self.offset.x,
            self.offset.y,
            Globals.display.get_width(),
            Globals.display.get_height(),
        )
