import pygame as pg

from ..utils import load_image


class ResourceManager:  # TODO add font to resource manager
    def __init__(self):
        self._images = {}
        self._sprite_sheets = {}

    def get_image(self, path):
        resource = self._images.get(path, None)
        if resource is None:
            self._images.setdefault(path, load_image(path))
        return self._images.get(path)

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
