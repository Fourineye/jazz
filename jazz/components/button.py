import pygame
from typing import Callable

from .sprite import Sprite
from .label import Label
from .. import Globals
from ..primatives import Draw
from ..utils import Color, Rect, Vec2, Surface
from pygame._sdl2 import Texture


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
            unpressed_color (tuple | Color, optional): Custom unpressed color. Defaults to azure blue.
            pressed_color (tuple | Color, optional): Custom pressed color. Defaults to deep ocean blue.
            hover_color (tuple | Color, optional): Custom hover color. Defaults to active blue.
            radius (int, optional): Corner rounding radius for the button background. Defaults to 6.
            style (str, optional): Styling paradigm: "flat", "skeuomorphic", "gradient", "glossy". Defaults to "skeuomorphic".
            shadow_offset (tuple, optional): X and Y offset for the button shadow. Defaults to (1, 2).
            shadow_color (tuple | Color, optional): Color of the button shadow. Defaults to black with alpha 80.
            shadow_blur (int, optional): Soft blur step size of the button shadow. Defaults to 2.
            border_color (tuple | Color, optional): Border outline color. Defaults to None.
            border_width (int, optional): Border stroke thickness. Defaults to 0.
            text_color (tuple | Color, optional): Color of the button label text. Defaults to white.
        """
        super().__init__(name, **kwargs)
        self.screen_space = True

        self._callback = kwargs.get("callback", None)
        self._on_release = kwargs.get("on_release", True)

        self._size = Vec2(kwargs.get("size", (10, 10)))
        self._hardware_offset()

        self._unpressed_asset = kwargs.get("unpressed", None)
        self._pressed_asset = kwargs.get("pressed", None)
        self._hover_asset = kwargs.get("hover", None)

        self.last_state = self.UNPRESSED
        self.state = self.UNPRESSED

        self._label = kwargs.get("label", None)
        if self._label is not None:
            text_size = kwargs.get("text_size", 12)
            text_color = kwargs.get("text_color", Color("white"))
            self._label = Label(
                text=self._label, text_color=text_color, fontsize=text_size
            )
            self.add_child(self._label)

        self._is_styled = False
        if self._unpressed_asset is None:
            self._is_styled = True
            self._kwargs = kwargs.copy()
            radius = kwargs.get("radius", 6)
            style = kwargs.get("style", "skeuomorphic")
            shadow_offset = kwargs.get("shadow_offset", (1, 2))
            shadow_color = kwargs.get("shadow_color", Color(0, 0, 0, 80))
            shadow_blur = kwargs.get("shadow_blur", 2)
            border_color = kwargs.get("border_color", None)
            border_width = kwargs.get("border_width", 0)

            unpressed_color = kwargs.get("unpressed_color", kwargs.get("unpressed", Color(60, 120, 210)))
            pressed_color = kwargs.get("pressed_color", kwargs.get("pressed", Color(40, 80, 150)))
            hover_color = kwargs.get("hover_color", kwargs.get("hover", Color(80, 140, 230)))

            self._unpressed_asset = Globals.resource.get_styled_texture(
                self._size, unpressed_color, radius, shadow_offset, shadow_color, shadow_blur, style, border_color, border_width
            )
            self._pressed_asset = Globals.resource.get_styled_texture(
                self._size, pressed_color, radius, shadow_offset, shadow_color, shadow_blur, style, border_color, border_width
            )
            self._hover_asset = Globals.resource.get_styled_texture(
                self._size, hover_color, radius, shadow_offset, shadow_color, shadow_blur, style, border_color, border_width
            )
        else:
            if self._pressed_asset is None:
                self._pressed_asset = Globals.resource.get_color(Color(128, 128, 128))
            if self._hover_asset is None:
                self._hover_asset = Globals.resource.get_color(Color(192, 192, 192))

        self.texture = self._unpressed_asset

    def on_load(self) -> None:
        """Initializes target position bounds and updates nested child label positions on scene mount."""
        super().on_load()
        if self._label is not None:
            self._label.pos = self.rect.center

    def update(self, _delta: float) -> None:
        """Monitors mouse cursor interaction events to resolve button hover and click states.

        Args:
            _delta (float): Unused engine timing delta value.
        """
        mouse_pos = Globals.mouse.pos
        if self.visible:
            if self.rect.collidepoint(mouse_pos):
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

    @property
    def texture(self):
        """Texture | Image: Gets the active Texture or Image asset."""
        return self._texture

    @texture.setter
    def texture(self, new_texture) -> None:
        """Sets the texture asset, preserving the logical size of the button."""
        logical_size = Vec2(self._size) if hasattr(self, "_size") else None
        Sprite.texture.fset(self, new_texture)
        if getattr(self, "_is_styled", False) and logical_size is not None:
            self._size = logical_size
            self._hardware_offset()

    def render(self, offset: Vec2) -> None:
        """Draws the button background texture and children.

        Args:
            offset (Vec2): Viewport rendering offset to apply.
        """
        if not self.visible:
            return
            
        if getattr(self, "_is_styled", False) and self.texture is not None:
            shadow_offset = self._kwargs.get("shadow_offset", (1, 2))
            shadow_blur = self._kwargs.get("shadow_blur", 2)
            pad_x = abs(shadow_offset[0]) + shadow_blur * 2
            pad_y = abs(shadow_offset[1]) + shadow_blur * 2
            
            dest_pos = self.draw_pos + offset - Vec2(pad_x, pad_y).elementwise() * self._scale
            dest_size = Vec2(self.texture.width, self.texture.height).elementwise() * self._scale
            dest = Rect(dest_pos, dest_size)
            
            if isinstance(self.texture, Texture):
                origin = -self._draw_offset + Vec2(pad_x, pad_y).elementwise() * self._scale
                self.texture.draw(
                    None,
                    dest,
                    self.rotation,
                    origin,
                    self.flip_x,
                    self.flip_y,
                )
            else:
                self.texture.flip_x = self.flip_x
                self.texture.flip_y = self.flip_y
                self.texture.angle = -self.rotation
                self.texture.alpha = self._alpha
                self.texture.draw(None, dest)
        else:
            super().render(offset)

    def render_debug(self, offset: Vec2):
        """Draws the active bounding box around the button in debug mode.

        Args:
            offset (Vec2): Screen space render offset.
        """
        super().render_debug(offset)
        Draw.rect(self.rect.move(offset), Color("green"), 3)
