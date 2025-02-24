import pygame
from pygame._sdl2 import Texture

from .sprite import Sprite
from ..utils import Vec2, map_range, Rect
from ..global_dict import Globals
from ..primatives import Draw


class ProgressBar(Sprite):
    def __init__(self, value, max_value, **kwargs):
        kwargs.setdefault("name", "Progress Bar")
        super().__init__(**kwargs)
        self.size = kwargs.get("size", Vec2(200, 50))
        self.value = value
        self.max_value = max_value
        self.bg_color = kwargs.get("bg_color", (100, 100, 100))
        self.color = kwargs.get("color", (100, 100, 200))
        self.line_color = kwargs.get("line_color", (50, 50, 50))
        self.radius = kwargs.get("radius", 0)
        self.line_width = kwargs.get("line_width", 3)
        self.update_bar()

    def update_bar(self):
        self.texture = Texture(Globals.renderer, self.size, target=True)
        texture_rect = self.texture.get_rect()
        with Draw.canvas(self.texture):
            Draw.fill_rect(texture_rect, self.bg_color)
            if self.value > 0:
                fill_height = texture_rect.height - self.line_width * 2
                fill_width = map_range(
                    self.value,
                    0,
                    self.max_value,
                    0,
                    texture_rect.width - self.line_width * 2,
                )
                fill_rect = Rect(
                    self.line_width, self.line_width, fill_width, fill_height
                )
                Draw.fill_rect(fill_rect, self.color)
            if self.line_width > 0:
                Draw.rect(texture_rect, self.line_color, self.line_width)

    def update_value(self, value):
        self.value = value
        self.update_bar()

    def update_max_value(self, max_value):
        self.max_value = max_value
        self.update_bar()
