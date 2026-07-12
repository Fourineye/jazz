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


def _default() -> Surface:
    """Generates a default checkerboard magenta/gray Surface fallback asset.

    Returns:
        Surface: The default fallback Surface.
    """
    default = Surface((10, 10))
    default.fill("magenta")
    pygame.draw.rect(default, "gray", (5, 0, 5, 5))
    pygame.draw.rect(default, "gray", (0, 5, 5, 5))
    return default


class ResourceManager:
    """Manages system and game assets (surfaces, textures, colors, sprite sheets, and fonts).

    Optimizes asset usage by caching loaded resources.
    """
    DEFAULT_FONT = INTERNAL_PATH + "/resources/Roboto-Regular.ttf"

    def __init__(self, renderer: Renderer):
        """Initializes the ResourceManager with standard default fallbacks.

        Args:
            renderer (Renderer): The hardware renderer used to compile Textures.
        """
        self._surfaces: dict[str, Surface] = {"default": _default()}
        self._textures: dict[str, Texture | Image] = {
            "default": Texture.from_surface(renderer, _default())
        }
        self._colors: dict[tuple[int, int, int], Texture] = {}
        self._sprite_sheets: dict[str, list[Image | Texture]] = {}
        self._fonts: dict[str, dict[int, pygame.Font]] = {}

    def clear(self) -> None:
        """Destroys any loaded images, fonts, and spritesheets."""
        self._surfaces.clear()
        self._textures.clear()
        self._surfaces = {"default": _default()}
        self._textures = {
            "default": Texture.from_surface(Globals.renderer, _default())
        }
        self._colors.clear()
        self._sprite_sheets.clear()
        self._fonts.clear()

    def get_font(self, id: str = DEFAULT_FONT, size: int = 12) -> pygame.font.Font:
        """Loads and returns a cached font from the filesystem.

        Args:
            id (str, optional): File path to the font. Defaults to DEFAULT_FONT.
            size (int, optional): The font size. Defaults to 12.

        Returns:
            Font: The cached or loaded Pygame Font object.
        """
        if id not in self._fonts.keys():
            self._fonts[id] = {}
        font = self._fonts[id].get(size, None)
        if font is None:
            font = pygame.font.Font(id, size)
            self._fonts[id].setdefault(size, font)
        return font

    def get_texture(self, id: str) -> Texture | Image:
        """Retrieves or loads a cached hardware-accelerated Texture.

        Args:
            id (str): File path of the image texture.

        Returns:
            Texture | Image: The hardware-accelerated Texture.
        """
        resource = self._textures.get(id, None)
        if resource is None:
            resource = load_texture(id)
            self._textures.setdefault(id, resource)
        return resource

    def add_texture(
        self, texture: Surface | Texture | Image, id: str, force: bool = False
    ) -> Texture | Image:
        """Manually registers an image/texture under a unique ID.

        Args:
            texture (Surface | Texture | Image): The texture source to add.
            id (str): The identifier key to register the texture under.
            force (bool, optional): Overwrite the texture if it already exists. Defaults to False.

        Returns:
            Texture | Image: The registered Texture object.
        """
        if force or id not in self._textures.keys():
            if isinstance(texture, (Texture, Image)):
                self._textures[id] = texture
            else:
                self._textures[id] = Texture.from_surface(
                    Globals.renderer, texture
                )
        return self._textures[id]

    def get_surface(self, id: str) -> Surface:
        """Retrieves or loads a cached software Surface.

        Args:
            id (str): File path of the image.

        Returns:
            Surface: The cached or loaded Pygame Surface.
        """
        resource = self._surfaces.get(id, None)
        if resource is None:
            resource = load_image(id)
            self._surfaces.setdefault(id, resource)
        return resource

    def add_surface(self, texture: Surface, id: str) -> Texture | Image:
        """Manually registers a software Surface under a unique ID.

        Args:
            texture (Surface): The Surface to add.
            id (str): The identifier key to register the surface under.

        Returns:
            Texture | Image: The texture equivalent of the surface.
        """
        if id not in self._surfaces.keys():
            self._surfaces[id] = texture
        return self._textures[id]

    def get_sprite_sheet(self, id: str) -> list[Image | Texture]:
        """Retrieves a pre-sliced sprite sheet list of textures.

        Args:
            id (str): The sprite sheet identifier key.

        Raises:
            JazzException: If the sprite sheet is not registered.

        Returns:
            list[Image | Texture]: List of textures/images making up the spritesheet.
        """
        resource = self._sprite_sheets.get(id, None)
        if resource is None:
            raise (JazzException(f"{id} is not a valid sprite sheet"))
        return resource

    def get_color(self, color: Color) -> Texture:
        """Gets or generates a single-pixel colored Texture to fill space.

        Args:
            color (Color): The Pygame Color swatch to generate.

        Returns:
            Texture: The single-pixel colored Texture.
        """
        resource = self._colors.get(color.rgb, None)
        if resource is None:
            colorSwatch = Surface((1, 1))
            colorSwatch.fill(color)
            resource = Texture.from_surface(Globals.renderer, colorSwatch)
            self._colors.setdefault(color.rgb, resource)

        return resource

    def make_sprite_sheet(
        self, id: str, dimensions: Vec2, offset: tuple[int, int] = (0, 0)
    ) -> list[Image | Texture]:
        """Loads, slices, and registers a grid-aligned sprite sheet of textures.

        Args:
            id (str): The texture path/id to load and slice.
            dimensions (Vec2): The width and height of each individual frame cell.
            offset (tuple[int, int], optional): Top-left start padding offset. Defaults to (0, 0).

        Returns:
            list[Image | Texture]: Sliced list of Image sub-textures.
        """
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
