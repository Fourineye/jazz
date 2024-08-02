from jazz import Globals, Label, Sprite
# import pygame


class TextBox(Label):
    def __init__(self, name="TextBox", **kwargs):
        super().__init__(name, **kwargs)
        self._blink_rate: float = kwargs.get("blink_rate", 0.25)
        self._blink: float = 0.0
        self._cursor = Label(
            font=self.font,
            text_color=self.text_color,
            text="|",
            anchor=(0, 1),
            pos=(self._draw_offset[0] + self.source.get_width(), self._draw_offset[1] + self.source.get_height() / 2),
            visible=False
        )
        self.add_child(self._cursor)

        self._active: bool = False

    def update(self, delta: float):
        if self._active:
            self._blink += delta
            if self._blink >= self._blink_rate:
                self._blink -= self._blink_rate
                self._cursor.visible = not self._cursor.visible

            if Globals.input.text:
                self.set_text(self.text_content + Globals.input.text)
            elif Globals.key.press("backspace"):
                self.set_text(self.text_content[:-1])
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
        super().set_text(text)
        self._cursor.local_pos = (self._draw_offset[0] + self.source.get_width(), self._draw_offset[1] + self.source.get_height() / 2)


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

