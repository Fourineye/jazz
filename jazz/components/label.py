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
        self.texture = self.font.render(
            self.text_content, True, self.text_color
        )

    def set_text(self, text):
        if not isinstance(text, str):
            text = str(text)
        if self.text_content != text:
            self.text_content = text
            self.texture = self.font.render(text, True, self.text_color)

    def append_text(self, text):
        self.text_content += text
        self.set_text(self.text_content)

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, new_texture):
        if not Globals.app.experimental:
            self._texture = new_texture
            self._img_updated = False
            self.update_image()
        else:
            if not isinstance(
                new_texture, (pygame._sdl2.Texture, pygame._sdl2.Image)
            ):
                new_texture = pygame._sdl2.Texture.from_surface(
                    Globals.renderer, new_texture
                )
            self._texture = new_texture
            if isinstance(self._texture, pygame._sdl2.Image):
                self.render = self._render_hardware_image
                self._size = Vec2(self._texture.get_rect().size)
            else:
                self.render = self._render_hardware_texture
                self._size = Vec2(self._texture.width, self._texture.height)
            self._hardware_offset()
