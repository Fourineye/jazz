import pygame
from .sprite import Sprite
from .label import Label
from ..global_dict import Globals
from ..utils import Color, Rect, Surface, Vec2

class TextBox(Sprite):
    def __init__(self, name="TextBox", **kwargs):
        font = kwargs.get("font", None)
        if font is None:
            font_size = kwargs.get("fontsize", 24)
            font = Globals.resource.get_font(size=font_size)
        
        text_color = kwargs.get("text_color", Color(255, 255, 255))
        text = kwargs.get("text", " ")
        
        if "texture" not in kwargs:
            if "size" in kwargs:
                size = Vec2(kwargs["size"])
            else:
                if text.strip():
                    size = Vec2(font.size(text)) + (10, 10)
                else:
                    size = Vec2(150, font.get_height() + 10)
            box = Surface(size)
            box.fill(kwargs.get("bg_color", Color(32, 32, 32)))
            kwargs["texture"] = box
            
        super().__init__(name, **kwargs)
        
        self._text = Label(
            font=font,
            text_color=text_color,
            text=text,
            pos=(self._draw_offset[0] + 5, self._draw_offset[1] + self._size.y / 2),
            anchor=(0, 1)
        )
        self.add_child(self._text)

        self._cursor = Label(
            font=font,
            text_color=text_color,
            text="|",
            anchor=(0, 1),
            pos=(self._draw_offset[0] + self._size.x, self._draw_offset[1] + self._size.y / 2),
            visible=False
        )
        self.add_child(self._cursor)

        self._blink_rate: float = kwargs.get("blink_rate", 0.25)
        self._blink: float = 0.0
        self._active: bool = False
        
        self._on_submit = kwargs.get("on_submit", None)
        self._on_change = kwargs.get("on_change", None)
        
        # Initialize cursor position
        self.set_text(text)

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, val: bool):
        if self._active != val:
            self._active = val
            self._blink = 0.0
            self._cursor.visible = val
            if val:
                Globals.input.start_text_input()
            else:
                Globals.input.stop_text_input()

    def update(self, delta: float):
        if self.active:
            self._blink += delta
            if self._blink >= self._blink_rate:
                self._blink -= self._blink_rate
                self._cursor.visible = not self._cursor.visible

            # Handle text input
            if Globals.input.text:
                self.set_text(self._text.text_content + Globals.input.text)
                self._blink = 0.0
                self._cursor.visible = True

            # Handle backspace
            if Globals.key.press("backspace"):
                self.set_text(self._text.text_content[:-1])
                self._blink = 0.0
                self._cursor.visible = True

            # Handle enter
            if Globals.key.press("enter"):
                self.active = False
                if callable(self._on_submit):
                    self._on_submit(self._text.text_content)

            # Deactivate if user clicks outside
            if Globals.mouse.click(0) and not self.rect.collidepoint(Globals.mouse.pos):
                self.active = False
        else:
            if Globals.mouse.click(0) and self.rect.collidepoint(Globals.mouse.pos):
                self.active = True

    def set_text(self, text):
        old_text = self._text.text_content
        self._text.set_text(text)
        self._cursor.local_pos = (
            self._text.local_pos.x + self._text._size.x,
            self._text.local_pos.y
        )
        if old_text != text and callable(self._on_change):
            self._on_change(text)

    @property
    def text(self) -> str:
        return self._text.text_content

    @text.setter
    def text(self, new_text: str):
        self.set_text(new_text)
