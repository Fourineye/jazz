import pygame


from .sprite import Sprite
from ..global_dict import Globals
from ..utils import Vec2


class Label(Sprite):
    def __init__(self, name="label", **kwargs):
        super().__init__(name, **kwargs)
        font_size = kwargs.get("fontsize", 24)

        self.font = kwargs.get(
            "font", Globals.resource.get_font(size=font_size)
        )
        self.text_color = kwargs.get("text_color", (255, 255, 255))

        self.text_content = kwargs.get("text", " ")
        if self.text_content:
            self.texture = self.font.render(
                self.text_content, True, self.text_color
            )
        else:
            self.texture = self.font.render(" ", True, self.text_color)
            self._size = Vec2(0, self._size.y)
            self._hardware_offset()

    def set_text(self, text):
        if not isinstance(text, str):
            text = str(text)
        if self.text_content != text:
            self.text_content = text
            if text:
                self.texture = self.font.render(text, True, self.text_color)
            else:
                self.texture = self.font.render(" ", True, self.text_color)
                self._size = Vec2(0, self._size.y)
                self._hardware_offset()

    def append_text(self, text):
        self.text_content += text
        self.set_text(self.text_content)
