import pygame

from ..utils import load_image, INTERNAL_PATH, load_texture, Surface, Rect
from ..global_dict import Globals


class ResourceManager:
    DEFAULT_FONT = INTERNAL_PATH + "/resources/Roboto-Regular.ttf"
    
    def __init__(self):
        default = Surface((10, 10))
        default.fill("magenta")
        pygame.draw.rect(default, "gray", (5,0,5,5))
        pygame.draw.rect(default, "gray", (0,5,5,5))
        self._images = {"default": default}
        self._textures = {"default":pygame._sdl2.Texture.from_surface(Globals.renderer, default)}
        self._sprite_sheets = {}
        self._fonts = {}

    def get_font(self, path: str = DEFAULT_FONT, size: int = 12):
        if path not in self._fonts.keys():
            self._fonts[path] = {}
        font = self._fonts.get(size, None)
        if font is None:
            font = pygame.font.Font(path, size)
            self._fonts.setdefault(size, font)
        return font

    def get_texture(self, path):
        resource = self._textures.get(path, None)
        if resource is None:
            resource = load_texture(path)
            self._textures.setdefault(path, resource)
        return resource

    def get_image(self, path):
        resource = self._images.get(path, None)
        if resource is None:
            resource = load_image(path)
            self._images.setdefault(path, resource)
        return resource

    def get_sprite_sheet(self, path):
        resource = self._sprite_sheets.get(path, None)
        if resource is None:
            raise (Exception(f"{path} is not a valid sprite sheet"))
        return resource

    def make_sprite_sheet(self, path, dimensions, offset=(0, 0)):
        sprite_sheet = self._sprite_sheets.get(path, None)
        if sprite_sheet is None:
            if Globals.app.experimental:
                sheet = self.get_texture(path)
            else:
                sheet = self.get_image(path)
            sprite_sheet = []
            size = sheet.get_rect().size
            x = offset[0]
            y = offset[1]
            while y < size[1] - 1:
                while x < size[0] - 1:
                    if Globals.app.experimental:
                        sprite = pygame._sdl2.Image(sheet, Rect((x,y), dimensions))
                    else:
                        sprite = sheet.subsurface((x, y), dimensions)
                    sprite_sheet.append(sprite)
                    x += dimensions[0]
                x = offset[0]
                y += dimensions[1]
            self._sprite_sheets[path] = sprite_sheet
        return sprite_sheet
