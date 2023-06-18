from random import randint

import pygame

from Jazz.global_dict import Game_Globals
from Jazz.utils import Vec2, clamp


class Camera:
    """Class that handles the drawing of objects onto the display."""

    STRICT = 0
    SMOOTH = 1

    def __init__(self):
        self.display = pygame.display.get_surface()
        self._bg_color = (0, 0, 0)
        self._blanking = True
        self.target = None
        self.bounds = None
        self.follow_type = self.STRICT
        self.offset = Vec2()
        self.shake = Vec2()
        self.magnitude = 0
        self.damping = 0.1
        self.display_center = (
            self.display.get_width() / 2,
            self.display.get_height() / 2,
        )
        self.debug = False

    def update(self, _delta):
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
                self.magnitude * randint(-10, 10), self.magnitude * randint(-10, 10)
            )
        else:
            self.shake = Vec2()
            self.magnitude = 0

    def render(self):
        draw_objects = list(Game_Globals["Scene"].values())
        draw_objects.sort(key=lambda obj: obj._z, reverse=False)

        if self._blanking:
            self.display.fill(self._bg_color)
        [
            (
                obj.draw(
                    self.display,
                    (self.offset + self.shake) if not obj.screen_space else None,
                ),
                obj.debug_draw(
                    self.display,
                    (self.offset + self.shake) if not obj.screen_space else None,
                )
                if self.debug
                else None,
            )
            if obj.visible
            else None
            for obj in draw_objects
        ]

    def update_offset(self):
        """Updates the Camera offset to the target."""
        if self.target is None:
            return
        offset_x, offset_y = self.offset
        if isinstance(self.target, Vec2):
            target_x = self.target.x
            target_y = self.target.y
        else:
            target_x, target_y = self.target.pos

        if self.follow_type == self.STRICT:
            offset_x = self.display_center[0] - target_x
            offset_y = self.display_center[1] - target_y
        elif self.follow_type == self.SMOOTH:
            offset_x += (self.display_center[0] - target_x - offset_x) / 5
            offset_y += (self.display_center[1] - target_y - offset_y) / 5

        if self.bounds is not None:
            offset_x = clamp(offset_x, -self.bounds.right, -self.bounds.left)
            offset_y = clamp(offset_y, -self.bounds.bottom, -self.bounds.top)

        self.offset.update(offset_x, offset_y)

    def set_offset(self, position=(0, 0)):
        """Sets the camera offset to a specified value

        Args:
            position (tuple, optional): New offset to set the Camera to. Defaults to (0, 0).
        """
        offset_x = self.display_center[0] - position[0]
        offset_y = self.display_center[1] - position[1]
        self.offset.update(offset_x, offset_y)

    def set_target(self, target):
        """
        Sets the target of the Camera, which it will follow.

        Args:
            target (Entity, Vec2): The target to follow.
        """
        if isinstance(target, Vec2):
            self.target = target
        elif isinstance(target, object):
            self.target = target
        else:
            print("Target must either be a Vec2 or an Entity")

    def set_bounds(self, bounds):
        if len(bounds) != 4:
            print("Bounds must be pygame rect or a iterable with length 4")
        if isinstance(bounds, pygame.Rect):
            self.bounds = bounds
        else:
            self.bounds = pygame.Rect(*bounds)

    def set_bg_color(self, color):
        self._bg_color = color

    def add_shake(self, magnitude):
        """
        Adds magnitude to the Camera shake.

        Args:
            magnitude (float): The magnitude of the shake to add.
        """
        self.magnitude = magnitude
        self.shake = Vec2()

    def sort(self, key=None):
        """
        Sorts the layers based on either the Camera key or one provided

        Args:
            key (str, optional): The name of an attribute to use to sort
                each layer. Defaults to None.
        """
        if key is None:
            self._background_layer.sort(key=lambda obj: getattr(obj, self.key, 0))
            self._foreground_layer.sort(key=lambda obj: getattr(obj, self.key, 0))
            self._screen_layer.sort(key=lambda obj: getattr(obj, self.key, 0))
        else:
            self._background_layer.sort(key=lambda obj: getattr(obj, key, 0))
            self._foreground_layer.sort(key=lambda obj: getattr(obj, key, 0))
            self._screen_layer.sort(key=lambda obj: getattr(obj, key, 0))

    def draw_check(self, obj, debug=False):
        draw = hasattr(obj, "debug_draw") if debug else hasattr(obj, "draw")
        return draw and getattr(obj, "visible", True)

    @property
    def pos(self):
        return self.display_center - self.offset
