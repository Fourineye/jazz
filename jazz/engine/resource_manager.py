import pygame

from pygame._sdl2 import Texture, Image, Renderer
from ..global_dict import Globals
from ..utils import (
    INTERNAL_PATH,
    Rect,
    Surface,
    Vec2,
    load_image,
    load_texture,
    Color,
    JazzException,
)


class ResourceManager:
    DEFAULT_FONT = INTERNAL_PATH + "/resources/Roboto-Regular.ttf"

    def __init__(self, renderer: Renderer):
        default = Surface((10, 10))
        default.fill("magenta")
        pygame.draw.rect(default, "gray", (5, 0, 5, 5))
        pygame.draw.rect(default, "gray", (0, 5, 5, 5))
        self._surfaces: dict[str, Surface] = {"default": default}
        self._textures: dict[str, Texture | Image] = {
            "default": Texture.from_surface(renderer, default)
        }
        self._colors: dict[tuple[int, int, int], Texture] = {}
        self._sprite_sheets: dict[str, list[Image]] = {}
        self._fonts: dict[str, dict[int, pygame.Font]] = {}

    def clear(self) -> None:
        """Destroys any loaded images, fonts, and spritesheets."""
        self._surfaces.clear()
        self._textures.clear()
        default = Surface((10, 10))
        default.fill("magenta")
        pygame.draw.rect(default, "gray", (5, 0, 5, 5))
        pygame.draw.rect(default, "gray", (0, 5, 5, 5))
        self._surfaces = {"default": default}
        self._textures = {
            "default": Texture.from_surface(Globals.renderer, default)
        }
        self._colors.clear()
        self._sprite_sheets.clear()
        self._fonts.clear()

    def get_font(self, id: str = DEFAULT_FONT, size: int = 12):
        if id not in self._fonts.keys():
            self._fonts[id] = {}
        font = self._fonts.get(size, None)
        if font is None:
            font = pygame.font.Font(id, size)
            self._fonts.setdefault(size, font)
        return font

    def get_texture(self, id: str) -> Texture | Image:
        resource = self._textures.get(id, None)
        if resource is None:
            resource = load_texture(id)
            self._textures.setdefault(id, resource)
        return resource

    def add_texture(
        self, texture: Surface | Texture | Image, id: str
    ) -> Texture | Image:
        if id not in self._textures.keys():
            if isinstance(texture, (Texture, Image)):
                self._textures[id] = texture
            else:
                self._textures[id] = Texture.from_surface(
                    Globals.renderer, texture
                )
        return self._textures[id]

    def get_surface(self, id: str):
        resource = self._surfaces.get(id, None)
        if resource is None:
            resource = load_image(id)
            self._surfaces.setdefault(id, resource)
        return resource

    def add_surface(self, texture: Surface, id: str):
        if id not in self._surfaces.keys():
            self._surfaces[id] = texture
        return self._textures[id]

    def get_sprite_sheet(self, id: str) -> list[Image]:
        resource = self._sprite_sheets.get(id, None)
        if resource is None:
            raise (JazzException(f"{id} is not a valid sprite sheet"))
        return resource

    def get_color(self, color: Color):
        resource = self._colors.get(color.rgb, None)
        if resource is None:
            colorSwatch = Surface((1, 1))
            colorSwatch.fill(color)
            resource = Texture.from_surface(Globals.renderer, colorSwatch)
            self._colors.setdefault(color.rgb, resource)

        return resource

    def make_sprite_sheet(
        self, id: str, dimensions: Vec2, offset=(0, 0)
    ) -> list[Image]:
        sprite_sheet = self._sprite_sheets.get(id, None)
        if sprite_sheet is None:
            sheet = self.get_texture(id)
            sprite_sheet = []
            size = sheet.get_rect().size
            x = offset[0]
            y = offset[1]
            while y < size[1] - 1:
                while x < size[0] - 1:
                    sprite = Image(sheet, Rect((x, y), dimensions))
                    sprite_sheet.append(sprite)
                    x += dimensions[0]
                x = offset[0]
                y += dimensions[1]
            self._sprite_sheets[id] = sprite_sheet
        return sprite_sheet
