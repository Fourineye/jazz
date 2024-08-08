import pygame

from .sprite import Sprite
from ..utils import Vec2, map_range


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
        # Draw the background color
        self.source = pygame.Surface(self.size)
        pygame.draw.rect(
            self.source,
            self.bg_color,
            self.source.get_rect(),
            border_radius=self.radius,
        )
        # Draw the bar fill
        if self.value > 0:
            fill_height = self.source.get_height() - self.line_width * 2
            fill_width = map_range(
                self.value,
                0,
                self.max_value,
                0,
                self.source.get_width() - self.line_width * 2,
                )
            fill_rect = pygame.Rect(
                self.line_width, self.line_width, fill_width, fill_height
            )
            pygame.draw.rect(self.source, self.color, fill_rect)
        # Draw the border
        if self.line_width > 0:
            pygame.draw.rect(
                self.source,
                self.line_color,
                self.source.get_rect(),
                self.line_width,
                border_radius=self.radius,
            )
        self._img_updated = False

    def update_value(self, value):
        self.value = value
        self.update_bar()

    def update_max_value(self, max_value):
        self.max_value = max_value
        self.update_bar()
