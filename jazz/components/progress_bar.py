import pygame

from .sprite import Sprite
from ..utils import Vec2, map_range, Rect, Texture
from ..global_dict import Globals
from ..primatives import Draw


class ProgressBar(Sprite):
    """UI Component representing a progress or health bar using target texture drawing."""

    def __init__(self, value: float | int, max_value: float | int, **kwargs) -> None:
        """Initializes the ProgressBar component.

        Args:
            value (float | int): Current numeric value.
            max_value (float | int): Maximum numeric value.
            size (Vec2, optional): Dimensions of the progress bar. Defaults to Vec2(200, 50).
            bg_color (tuple | Color, optional): Background fill color. Defaults to gray.
            color (tuple | Color, optional): Active progress bar fill color. Defaults to blue.
            line_color (tuple | Color, optional): Outline border color. Defaults to dark gray.
            radius (int, optional): Corner rounding radius for the background and active progress fill. Defaults to 0.
            line_width (int, optional): Width of outline border in pixels. Defaults to 3.
        """
        kwargs.setdefault("name", "Progress Bar")
        super().__init__(**kwargs)
        self.size = Vec2(kwargs.get("size", (200, 50)))
        self._size = self.size
        self._hardware_offset()
        self.value = value
        self.max_value = max_value
        self.bg_color = kwargs.get("bg_color", (100, 100, 100))
        self.color = kwargs.get("color", (100, 100, 200))
        self.line_color = kwargs.get("line_color", (50, 50, 50))
        self.radius = kwargs.get("radius", 0)
        self.line_width = kwargs.get("line_width", 3)
        self.update_bar()

    def update_bar(self) -> None:
        """Re-renders the progress bar texture based on current values and colors."""
        w, h = int(self.size.x), int(self.size.y)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        
        bg_color = pygame.Color(self.bg_color)
        fill_color = pygame.Color(self.color)
        line_color = pygame.Color(self.line_color)
        
        # 1. Draw rounded background
        pygame.draw.rect(surf, bg_color, (0, 0, w, h), border_radius=self.radius)
        
        # 2. Draw progress fill with a subtle gradient and rounded masking
        if self.value > 0:
            fill_width = map_range(
                self.value,
                0,
                self.max_value,
                0,
                w - self.line_width * 2,
            )
            fill_height = h - self.line_width * 2
            
            if fill_width > 0 and fill_height > 0:
                fill_surf = pygame.Surface((int(fill_width), int(fill_height)), pygame.SRCALPHA)
                
                # Apply vertical lighting gradient for progress fill
                color_light = pygame.Color(
                    min(255, fill_color.r + 30),
                    min(255, fill_color.g + 30),
                    min(255, fill_color.b + 30),
                    fill_color.a
                )
                color_dark = pygame.Color(
                    max(0, fill_color.r - 30),
                    max(0, fill_color.g - 30),
                    max(0, fill_color.b - 30),
                    fill_color.a
                )
                
                for y in range(int(fill_height)):
                    ratio = y / max(1, fill_height - 1)
                    r = int(color_light.r + (color_dark.r - color_light.r) * ratio)
                    g = int(color_light.g + (color_dark.g - color_light.g) * ratio)
                    b = int(color_light.b + (color_dark.b - color_light.b) * ratio)
                    pygame.draw.line(fill_surf, pygame.Color(r, g, b, fill_color.a), (0, y), (int(fill_width), y))
                    
                # Apply rounded corner clipping
                fill_radius = max(0, self.radius - self.line_width)
                if fill_radius > 0:
                    mask = pygame.Surface((int(fill_width), int(fill_height)), pygame.SRCALPHA)
                    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, int(fill_width), int(fill_height)), border_radius=fill_radius)
                    fill_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                    
                surf.blit(fill_surf, (self.line_width, self.line_width))
                
        # 3. Draw border outline
        if self.line_width > 0:
            pygame.draw.rect(surf, line_color, (0, 0, w, h), self.line_width, border_radius=self.radius)
            
        self.texture = Texture.from_surface(Globals.renderer, surf)

    def update_value(self, value: float | int) -> None:
        """Updates the current progress value and re-renders the bar.

        Args:
            value (float | int): New current progress value.
        """
        self.value = value
        self.update_bar()

    def update_max_value(self, max_value: float | int) -> None:
        """Updates the maximum limit value and re-renders the bar.

        Args:
            max_value (float | int): New maximum limit value.
        """
        self.max_value = max_value
        self.update_bar()
