from contextlib import contextmanager

import pygame
from pygame._sdl2 import Texture

from .global_dict import Globals
from .utils import Rect, Color, Vec2, Surface


from collections.abc import Generator

class Draw:
    """Helper class for drawing geometric primitives.

    Supports hardware-accelerated drawing via SDL2 Renderer or software drawing
    via pygame.draw on Pygame Surfaces.
    """
    CIRCLE = [Vec2(1, 0).rotate(i * 10) for i in range(36)]
    target_surface: Surface = Surface((1, 1))
    hardware_draw: bool = False

    @staticmethod
    def init() -> None:
        """Initializes the drawing target to the main display surface and enables hardware rendering."""
        Draw.target_surface = Globals.display
        Draw.hardware_draw = True

    @staticmethod
    @contextmanager
    def canvas(texture: Texture | Surface) -> Generator[None, None, None]:
        """Context manager to temporarily redirect drawing operations to a specific target.

        Args:
            texture (Texture | Surface): The drawing destination. If it is a Texture,
                hardware rendering will be target-bound. If it is a Surface, software
                rendering will be used.
        """
        if isinstance(texture, Texture):
            Draw.hardware_draw = True
            Globals.renderer.target = texture
            try:
                yield None
            finally:
                Globals.renderer.target = None
        else:
            Draw.hardware_draw = False
            Draw.target_surface = texture
            try:
                yield None
            finally:
                Draw.target_surface = Globals.display
                Draw.hardware_draw = True

    @staticmethod
    def line(p1: Vec2, p2: Vec2, color: Color, w: int = 1) -> None:
        """Draws a straight line segment.

        Args:
            p1 (Vec2): The starting point of the line.
            p2 (Vec2): The ending point of the line.
            color (Color): The color of the line.
            w (int, optional): The width of the line in pixels. Defaults to 1.
        """
        if Draw.hardware_draw:
            Globals.renderer.draw_color = color
            if w == 1:
                Globals.renderer.draw_line(p1, p2)
            else:
                for x in range(-w // 2, w // 2):
                    for y in range(-w // 2, w // 2):
                        if x**2 + y**2 <= (w // 2) ** 2:
                            Globals.renderer.draw_line(
                                p1 + Vec2(x, y), p2 + Vec2(x, y)
                            )
        else:
            pygame.draw.line(Draw.target_surface, color, p1, p2, w)

    @staticmethod
    def lines(points: list[Vec2], color: Color, w: int = 1, closed: bool = False) -> None:
        """Draws multiple connected line segments.

        Args:
            points (list[Vec2]): List of vertices defining the path.
            color (Color): The color of the lines.
            w (int, optional): The width of the lines in pixels. Defaults to 1.
            closed (bool, optional): Whether to connect the last vertex back to the first. Defaults to False.
        """
        if Draw.hardware_draw:
            for i in range(1, len(points)):
                Draw.line(points[i - 1], points[i], color, w)
            if closed:
                Draw.line(points[-1], points[0], color, w)
        else:
            pygame.draw.lines(Draw.target_surface, color, closed, points, w)

    @staticmethod
    def rect(rect: Rect | tuple[int, int, int, int], color: Color, w: int = 1) -> None:
        """Draws an unfilled rectangle.

        Args:
            rect (Rect | tuple): The bounds of the rectangle.
            color (Color): The outline color.
            w (int, optional): The outline border width in pixels. Defaults to 1.
        """
        if Draw.hardware_draw:
            Globals.renderer.draw_color = color
            if not isinstance(rect, Rect):
                rect = Rect(*rect)
            for i in range(w):
                Globals.renderer.draw_rect(rect.inflate(-2 * i, -2 * i))
        else:
            pygame.draw.rect(Draw.target_surface, color, rect, w)

    @staticmethod
    def circle(center: Vec2, radius: int, color: Color, w: int = 1) -> None:
        """Draws an unfilled circle.

        Args:
            center (Vec2): The center coordinate of the circle.
            radius (int): The radius of the circle in pixels.
            color (Color): The outline color.
            w (int, optional): The outline border width in pixels. Defaults to 1.
        """
        if Draw.hardware_draw:
            Draw.lines(
                [center + x * radius for x in Draw.CIRCLE], color, w, True
            )
        else:
            pygame.draw.circle(Draw.target_surface, color, center, radius, w)

    @staticmethod
    def fill_rect(rect: Rect | tuple[int, int, int, int], color: Color) -> None:
        """Draws a filled rectangle.

        Args:
            rect (Rect | tuple): The bounds of the rectangle.
            color (Color): The fill color.
        """
        if Draw.hardware_draw:
            Globals.renderer.draw_color = color
            if not isinstance(rect, Rect):
                rect = Rect(*rect)
            Globals.renderer.fill_rect(rect)
        else:
            pygame.draw.rect(Draw.target_surface, color, rect)

    @staticmethod
    def fill_circle(center: Vec2, radius: int, color: Color) -> None:
        """Draws a filled circle.

        Args:
            center (Vec2): The center coordinate of the circle.
            radius (int): The radius of the circle in pixels.
            color (Color): The fill color.
        """
        if Draw.hardware_draw:
            Globals.renderer.draw_color = color
            for i in range(len(Draw.CIRCLE)):
                Globals.renderer.fill_triangle(
                    center,
                    center + Draw.CIRCLE[i] * radius,
                    center + Draw.CIRCLE[(i + 1) % len(Draw.CIRCLE)] * radius,
                )
        else:
            pygame.draw.circle(Draw.target_surface, color, center, radius)
