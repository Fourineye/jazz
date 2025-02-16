from .global_dict import Globals
from .components import Label, Sprite
from .user_interface import DEFAULT_FONT
from .utils import Color, Rect, Surface, Vec2


class TextBox(Sprite):
    def __init__(self, name="TextBox", **kwargs):
        super().__init__(name, **kwargs)
        font = kwargs.get("font", DEFAULT_FONT)
        text_color = kwargs.get("text_color", Color(255, 255, 255))
        text = kwargs.get("text", " ")
        if not kwargs.get("texture", False):
            size = kwargs.get("size", Vec2(font.size(text)) + (10, 10))
            box = Surface(size)
            box.fill(kwargs.get("bg_color", Color(32, 32, 32)))
            self.texture = box
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

    def update(self, delta: float):
        if self._active:
            self._blink += delta
            if self._blink >= self._blink_rate:
                self._blink -= self._blink_rate
                self._cursor.visible = not self._cursor.visible

            if Globals.input.text:
                self.set_text(self._text.text_content + Globals.input.text)
            elif Globals.key.press("backspace"):
                self.set_text(self._text.text_content[:-1])
            elif not self.rect.collidepoint(Globals.mouse.pos):
                if Globals.mouse.click(0):
                    self._cursor.visible = False
                    self._active = False
            elif Globals.key.press("enter"):
                self._active = False
                self._cursor.visible = False
        else:
            if self.rect.collidepoint(Globals.mouse.pos):
                if Globals.mouse.click(0):
                    self._active = True

    def set_text(self, text):
        self._text.set_text(text)
        self._cursor.local_pos = (
            self._text._draw_offset[0] + self._text.texture.get_rect().w,
            self._text._draw_offset[1] + self._text.texture.get_rect().h / 2
        )


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

