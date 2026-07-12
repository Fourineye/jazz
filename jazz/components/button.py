import pygame
from typing import Callable

from .sprite import Sprite
from .label import Label
from .. import Globals
from ..primatives import Draw
from ..utils import Color, Rect, Vec2, Surface


class Button(Sprite):
    """Event-driven interactive Button UI component supporting unpressed, hover, and pressed states."""
    STATES = ["UNPRESSED", "HOVER", "PRESSED"]
    UNPRESSED = 0
    HOVER = 1
    PRESSED = 2

    def __init__(self, name: str = "button", **kwargs) -> None:
        """Initializes the Button component.

        Args:
            name (str, optional): The name of the button. Defaults to "button".
            callback (callable, optional): Callback executed on press/release events. Defaults to None.
            on_release (bool, optional): Execute callback when releasing button. Defaults to True.
            size (tuple, optional): Width and height of the button bounds. Defaults to (10, 10).
            unpressed (Texture, optional): Render asset for default state. Defaults to white color block.
            pressed (Texture, optional): Render asset for pressed state. Defaults to dark gray color block.
            hover (Texture, optional): Render asset for hover state. Defaults to light gray color block.
            label (str, optional): Custom label text layout inside button bounds. Defaults to None.
            text_size (int, optional): Size of font to display. Defaults to 12.
        """
        super().__init__(name, **kwargs)
        self.screen_space = True

        self._callback = kwargs.get("callback", None)
        self._on_release = kwargs.get("on_release", True)

        self._size = Vec2(kwargs.get("size", (10, 10)))
        self._rect = Rect((0, 0), self._size)
        self._hardware_offset()

        self._unpressed_asset = kwargs.get("unpressed", None)
        self._pressed_asset = kwargs.get("pressed", None)
        self._hover_asset = kwargs.get("hover", None)

        self.last_state = self.UNPRESSED
        self.state = self.UNPRESSED

        self._label = kwargs.get("label", None)
        if self._label is not None:
            text_size = kwargs.get("text_size", 12)
            self._label = Label(
                text=self._label, text_color=Color("black"), fontsize=text_size
            )
            self.add_child(self._label)

        if self._unpressed_asset is None:
            self._unpressed_asset = Globals.resource.get_color(
                Color(255, 255, 255)
            )
        if self._pressed_asset is None:
            self._pressed_asset = Globals.resource.get_color(
                Color(128, 128, 128)
            )
        if self._hover_asset is None:
            self._hover_asset = Globals.resource.get_color(
                Color(192, 192, 192)
            )

        self._texture = self._unpressed_asset

    def on_load(self) -> None:
        """Initializes target position bounds and updates nested child label positions on scene mount."""
        super().on_load()
        self._rect.topleft = self.draw_pos
        if self._label is not None:
            self._label.pos = self._rect.center

    def update(self, _delta: float) -> None:
        """Monitors mouse cursor interaction events to resolve button hover and click states.

        Args:
            _delta (float): Unused engine timing delta value.
        """
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

    def set_callback(self, callback: Callable[[], None]) -> None:
        """Registers a callback method to trigger when the button is clicked.

        Args:
            callback (callable): The callback function.
        """
        self._callback = callback

    def render_debug(self, offset: Vec2):
        """Draws the active bounding box around the button in debug mode.

        Args:
            offset (Vec2): Screen space render offset.
        """
        super().render_debug(offset)
        Draw.rect(self._rect.move(offset), Color("green"), 3)
