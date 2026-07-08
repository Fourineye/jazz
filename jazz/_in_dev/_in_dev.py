from ..global_dict import Globals
from ..components import Label, Sprite, TextBox
from ..utils import Color, Rect, Surface, Vec2


# class CheckBox(Sprite):
#     def __init__(self, name="CheckBox", **kwargs):
#         source = Surface((16, 16))
#         source.fill((10, 10, 25))
#         pygame.draw.circle(source, (20, 20, 40), (7, 7), 8)
#         pygame.draw.rect(source, (128, 128, 128), (0, 0, 16, 16), 1)
#         super().__init__(name, asset=source, **kwargs)
#         self._checkmark = jazz.Surface((24, 16))
#         pygame.draw.lines(
#             self._checkmark, (64, 128, 64), False, ((0, 8), (8, 16), (16, 0))
#         )
#         self.checked = False
#
#     def update(self, delta):
#         if self.rect.collidepoint(Globals.mouse.pos):
#             if Globals.mouse.click(0):
#                 self.checked = not self.checked

    # def draw(self, surface, offset=None):
    #     ...

