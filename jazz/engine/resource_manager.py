import pygame

from pygame._sdl2 import Texture, Image
from ..global_dict import Globals
from ..utils import INTERNAL_PATH, Rect, Surface, Vec2, load_image, load_texture


class ResourceManager:
    DEFAULT_FONT = INTERNAL_PATH + "/resources/Roboto-Regular.ttf"

    def __init__(self):
        default = Surface((10, 10))
        default.fill("magenta")
        pygame.draw.rect(default, "gray", (5, 0, 5, 5))
        pygame.draw.rect(default, "gray", (0, 5, 5, 5))
        self._images = {"default": default}
        self._textures = {
            "default": Texture.from_surface(Globals.renderer, default)
        }
        self._sprite_sheets = {}
        self._fonts = {}

    def get_font(self, id: str = DEFAULT_FONT, size: int = 12):
        if id not in self._fonts.keys():
            self._fonts[id] = {}
        font = self._fonts.get(size, None)
        if font is None:
            font = pygame.font.Font(id, size)
            self._fonts.setdefault(size, font)
        return font

    def get_texture(self, id: str):
        resource = self._textures.get(id, None)
        if resource is None:
            resource = load_texture(id)
            self._textures.setdefault(id, resource)
        return resource

    def add_texture(self, texture: Surface | Texture, id: str):
        if id not in self._textures.keys():
            if isinstance(texture, Texture):
                self._textures[id] = texture
            else:
                self._textures[id] = Texture.from_surface(
                    Globals.renderer, texture
                )

    def get_image(self, id: str):
        resource = self._images.get(id, None)
        if resource is None:
            resource = load_image(id)
            self._images.setdefault(id, resource)
        return resource

    def add_image(self, texture: Surface, id: str):
        if id not in self._images.keys():
            self._textures[id] = texture

    def get_sprite_sheet(self, id: str):
        resource = self._sprite_sheets.get(id, None)
        if resource is None:
            raise (Exception(f"{id} is not a valid sprite sheet"))
        return resource

    def make_sprite_sheet(self, id: str, dimensions: Vec2, offset=(0, 0)):
        sprite_sheet = self._sprite_sheets.get(id, None)
        if sprite_sheet is None:
            if Globals.app.experimental:
                sheet = self.get_texture(id)
            else:
                sheet = self.get_image(id)
            sprite_sheet = []
            size = sheet.get_rect().size
            x = offset[0]
            y = offset[1]
            while y < size[1] - 1:
                while x < size[0] - 1:
                    if Globals.app.experimental:
                        sprite = Image(sheet, Rect((x, y), dimensions))
                    else:
                        sprite = sheet.subsurface((x, y), dimensions)
                    sprite_sheet.append(sprite)
                    x += dimensions[0]
                x = offset[0]
                y += dimensions[1]
            self._sprite_sheets[id] = sprite_sheet
        return sprite_sheet
