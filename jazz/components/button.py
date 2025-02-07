import pygame

from .sprite import Sprite
from .. import Globals
from ..utils import Color, Rect, Vec2


class Button(Sprite):
    STATES = ["UNPRESSED", "HOVER", "PRESSED"]
    UNPRESSED = 0
    HOVER = 1
    PRESSED = 2

    def __init__(self, name="button", **kwargs):
        super().__init__(name, **kwargs)
        self.screen_space = True

        self._callback = kwargs.get("callback", None)
        self._on_release = kwargs.get("on_release", True)

        self._size = Vec2(kwargs.get("size", (10, 10)))
        self._rect = pygame.Rect((0, 0), self._size)
        self._hardware_offset()

        self._unpressed_asset = kwargs.get("unpressed", None)
        self._pressed_asset = kwargs.get("pressed", None)
        self._hover_asset = kwargs.get("hover", None)

        self.last_state = self.UNPRESSED
        self.state = self.UNPRESSED

        if self._unpressed_asset is None:
            self._unpressed_asset = Globals.scene.resource_manager.get_color(Color(255, 255, 255))
        if self._pressed_asset is None:
            self._pressed_asset = Globals.scene.resource_manager.get_color(Color(128, 128, 128))
        if self._hover_asset is None:
            self._hover_asset = Globals.scene.resource_manager.get_color(Color(192, 192, 192))

        self._texture = self._unpressed_asset

    def on_load(self):
        super().on_load()
        self._rect.topleft = self.draw_pos

    def update(self, _delta):
        mouse_pos = Globals.mouse.pos
        if self.visible:
            if self._rect.collidepoint(mouse_pos):
                if Globals.mouse.click(0):
                    self.state = self.PRESSED
                elif self.state != self.PRESSED or not Globals.mouse.held(0):
                    self.state = self.HOVER
            else:
                if self.state == self.PRESSED:
                    if not Globals.mouse.held(0):
                        self.state = self.UNPRESSED
                else:
                    self.state = self.UNPRESSED
            if self.last_state != self.state:
                if self.state == self.UNPRESSED:
                    if self._unpressed_asset is not None:
                        self._texture = self._unpressed_asset
                elif self.state == self.HOVER:
                    if self._hover_asset is not None:
                        self._texture = self._hover_asset
                    if (
                        callable(self._callback)
                        and self._on_release
                        and self.last_state == self.PRESSED
                    ):
                        self._callback()
                elif self.state == self.PRESSED:
                    if self._pressed_asset is not None:
                        self._texture = self._pressed_asset
                    if callable(self._callback) and not self._on_release:
                        self._callback()
            self.last_state = self.state

    def set_callback(self, callback):
        self._callback = callback

    def _render_hardware_texture(self, offset: Vec2):
        dest = Rect(
            self.draw_pos + offset, self._size.elementwise() * self._scale
        )
        self._texture.draw(
            None,
            dest,
            self.rotation,
            -self._draw_offset,
            self.flip_x,
            self.flip_y,
        )

    def _debug_hardware(self, offset: Vec2):
        super()._debug_hardware(offset)
        Globals.renderer.draw_rect(self._rect.move(offset))
