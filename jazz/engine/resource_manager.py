import pygame as pg

from ..utils import load_image, INTERNAL_PATH, load_texture


class ResourceManager:
    DEFAULT_FONT = INTERNAL_PATH + "/resources/Roboto-Regular.ttf"
    
    def __init__(self):
        self._images = {}
        self._textures = {}
        self._sprite_sheets = {}
        self._fonts = {}

    def get_font(self, path: str = DEFAULT_FONT, size: int = 12):
        if path not in self._fonts.keys():
            self._fonts[path] = {}
        font = self._fonts.get(size, None)
        if font is None:
            font = pg.font.Font(path, size)
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
            sheet = load_image(path)
            self._images[path] = sheet
            sprite_sheet = []
            size = sheet.get_size()
            x = offset[0]
            y = offset[1]
            while y < size[1] - 1:
                while x < size[0] - 1:
                    sprite = sheet.subsurface((x, y), dimensions)
                    sprite_sheet.append(sprite)
                    x += dimensions[0]
                x = offset[0]
                y += dimensions[1]
            self._sprite_sheets[path] = sprite_sheet
        return sprite_sheet
