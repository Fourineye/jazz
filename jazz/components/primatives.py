from typing import Iterable
from ..global_dict import Globals
from ..utils import Rect, Color, Vec2



class Primatives:
    CIRCLE = [Vec2(1, 0).rotate(i * 10) for i in range(36)]

    @staticmethod
    def line(p1: Vec2, p2: Vec2, color:Color, w: int=1):
        Globals.renderer.draw_color = color
        if w == 1:
            Globals.renderer.draw_line(p1, p2)
        else:
            for x in range(-w // 2, w //2):
                for y in range(-w // 2, w //2):
                    if x ** 2 + y ** 2 <= (w // 2) ** 2:
                        Globals.renderer.draw_line(p1 + Vec2(x,y), p2 + Vec2(x, y))

    @staticmethod
    def lines(points: Iterable[Vec2], color, w=1, closed=False):
        for i in range(1, len(points)):
            Primatives.line(points[i - 1], points[i], color, w)
        if closed:
            Primatives.line(points[-1], points[0], color, w)

    @staticmethod
    def rect(rect: Rect, color: Color, w=1):
        Globals.renderer.draw_color = color
        if not isinstance(rect, Rect):
            rect = Rect(*rect)
        for i in range(w):
            Globals.renderer.draw_rect(rect.inflate(-2 * i, -2 * i))

    @staticmethod
    def circle(center: Vec2, radius: int, color: Color, w: int = 1):
        Primatives.lines([center + x * radius for x in Primatives.CIRCLE], color, w, True)

    @staticmethod
    def fill_rect(rect: Rect, color: Color):
        Globals.renderer.draw_color = color
        if not isinstance(rect, Rect):
            rect = Rect(*rect)
        Globals.renderer.fill_rect(rect)
        
    @staticmethod
    def fill_circle(center: Vec2, radius: int, color: Color):
        Globals.renderer.draw_color = color
        for i in range(len(Primatives.CIRCLE)):
            Globals.renderer.fill_triangle(center, center + Primatives.CIRCLE[i] * radius, center + Primatives.CIRCLE[(i + 1) % len(Primatives.CIRCLE)] * radius)
