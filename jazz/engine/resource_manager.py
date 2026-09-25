"""ResourceManager that loads and caches textures, surfaces, fonts, sprite sheets, and custom resources."""

from typing import Any

import pygame
from pygame._sdl2 import Image, Renderer, Texture

from ..global_dict import Globals
from ..utils import (
    INTERNAL_PATH,
    Color,
    JazzException,
    Rect,
    Surface,
    Vec2,
    generate_styled_texture,
    load_image,
    load_texture,
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


_DEFAULT_SHADOW_COLOR = Color(0, 0, 0, 80)


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
        self._styled_textures: dict[tuple, Texture] = {}
        self._sprite_sheets: dict[str, list[Image | Texture]] = {}
        self._fonts: dict[str, dict[int, pygame.Font]] = {}
        self._animation_resources: dict[str, dict[str, Any]] = {}
        self._custom_resources: dict[str, dict[str, Any]] = {}

    def clear(self) -> None:
        """Destroys any loaded images, colors, styled textures, fonts, spritesheets,
        animations, and custom resources."""
        self._surfaces.clear()
        self._textures.clear()
        self._surfaces = {"default": _default()}
        self._textures = {
            "default": Texture.from_surface(Globals.renderer, _default())
        }
        self._colors.clear()
        self._styled_textures.clear()
        self._sprite_sheets.clear()
        self._fonts.clear()
        self._animation_resources.clear()
        self._custom_resources.clear()

    def get_font(self, id: str = DEFAULT_FONT, size: int = 12) -> pygame.font.Font:
        """Loads and returns a cached font from the filesystem.

        Args:
            id (str, optional): File path to the font. Defaults to DEFAULT_FONT.
            size (int, optional): The font size. Defaults to 12.

        Returns:
            Font: The cached or loaded Pygame Font object.
        """
        if id not in self._fonts:
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
        if force or id not in self._textures:
            if isinstance(texture, (Texture, Image)):
                self._textures[id] = texture
            else:
                self._textures[id] = Texture.from_surface(
                    Globals.renderer, texture
                )
        return self._textures[id]

    def remove_texture(self, id: str) -> None:
        """Removes a registered texture by ID if present.

        Args:
            id (str): The identifier key of the texture to remove.
        """
        self._textures.pop(id, None)

    def purge_sprite_textures(self, sprite_id: str) -> None:
        """Purges all dynamic textures registered for a given sprite ID.

        Args:
            sprite_id (str): The sprite object ID whose textures should be purged.
        """
        prefix = f"{sprite_id}:"
        keys_to_remove = {
            k
            for cache in (self._textures, self._surfaces, self._sprite_sheets)
            for k in cache
            if k == sprite_id or k.startswith(prefix)
        }
        for k in keys_to_remove:
            self._textures.pop(k, None)
            self._surfaces.pop(k, None)
            self._sprite_sheets.pop(k, None)

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

    def add_surface(self, texture: Surface, id: str) -> Surface:
        """Manually registers a software Surface under a unique ID.

        Args:
            texture (Surface): The Surface to add.
            id (str): The identifier key to register the surface under.

        Returns:
            Surface: The registered Pygame Surface.
        """
        if id not in self._surfaces:
            self._surfaces[id] = texture
        return self._surfaces[id]

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
        key = (color.r, color.g, color.b)
        resource = self._colors.get(key, None)
        if resource is None:
            colorSwatch = Surface((1, 1))
            colorSwatch.fill(color)
            resource = Texture.from_surface(Globals.renderer, colorSwatch)
            self._colors.setdefault(key, resource)

        return resource

    def get_styled_texture(
        self,
        size: tuple[int, int] | Vec2,
        color: Color,
        radius: int = 0,
        shadow_offset: tuple[int, int] = (0, 0),
        shadow_color: Color = _DEFAULT_SHADOW_COLOR,
        shadow_blur: int = 0,
        style: str = "flat",
        border_color: Color | None = None,
        border_width: int = 0,
    ) -> Texture:
        """Generates, caches, and returns a styled UI container background Texture.

        Args:
            size (tuple | Vec2): Dimensions of the main container.
            color (Color): Base fill color.
            radius (int, optional): Corner rounding radius. Defaults to 0.
            shadow_offset (tuple, optional): X and Y offset for the drop shadow. Defaults to (0, 0).
            shadow_color (Color, optional): Color of the drop shadow. Defaults to black with alpha 80.
            shadow_blur (int, optional): Soft blur step size of the drop shadow. Defaults to 0.
            style (str, optional): Styling paradigm: "flat", "skeuomorphic", "gradient", "glossy". Defaults to "flat".
            border_color (Color, optional): Border outline color. Defaults to None.
            border_width (int, optional): Border stroke thickness. Defaults to 0.

        Returns:
            Texture: The compiled hardware Texture.
        """
        w, h = int(size[0]), int(size[1])
        color = Color(color)
        shadow_color = Color(shadow_color)
        border_c_val = tuple(Color(border_color)) if border_color is not None else None
        
        key = (
            w, h,
            tuple(color),
            radius,
            shadow_offset[0], shadow_offset[1],
            tuple(shadow_color),
            shadow_blur,
            style,
            border_c_val,
            border_width
        )
        
        resource = self._styled_textures.get(key, None)
        if resource is not None:
            return resource
            
        resource = Texture.from_surface(Globals.renderer, generate_styled_texture(size, color, radius, shadow_offset, shadow_color, shadow_blur, style, border_color, border_width))
        self._styled_textures[key] = resource
        return resource

    def make_sprite_sheet(
        self,
        id: str,
        dimensions: Vec2 | tuple[int, int],
        offset: tuple[int, int] | Vec2 = (0, 0),
        spacing: tuple[int, int] | Vec2 = (0, 0),
    ) -> list[Image | Texture]:
        """Loads, slices, and registers a grid-aligned sprite sheet of textures.

        Frames are sub-regions of one texture. When a frame is drawn rotated or
        scaled, the renderer can sample texels just outside it, which shows the
        edge of the neighbouring frame as a thin line. Sheets used that way need
        transparent gaps between frames, sliced with `spacing`.

        Args:
            id (str): The texture path/id to load and slice.
            dimensions (Vec2 | tuple[int, int]): The width and height of each individual frame cell.
            offset (tuple[int, int] | Vec2, optional): Top-left start padding offset. Defaults to (0, 0).
            spacing (tuple[int, int] | Vec2, optional): Horizontal and vertical gap in pixels
                between neighbouring frames. Defaults to (0, 0).

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
                    x += dimensions[0] + spacing[0]
                x = offset[0]
                y += dimensions[1] + spacing[1]
            self._sprite_sheets[id] = sprite_sheet
        return sprite_sheet

    def add_animation_resource(
        self,
        id: str,
        spritesheet: str | list[str | Texture | Image | Surface],
        animation_frames: list[int] | None = None,
        animation_fps: int = 30,
        oneshot: bool = False,
    ) -> dict[str, Any]:
        """Registers a named animation resource packaging spritesheet, frame list, FPS, and loop mode.

        Args:
            id (str): Unique identifier for the animation resource.
            spritesheet (str | list): Spritesheet key or frame list.
            animation_frames (list[int], optional): Sequence indices of frames to play. Defaults to None.
            animation_fps (int, optional): Playback frame rate. Defaults to 30.
            oneshot (bool, optional): Loop disable flag. Defaults to False.

        Returns:
            dict[str, Any]: The registered animation configuration payload.
        """
        config = {
            "id": id,
            "spritesheet": spritesheet,
            "animation_frames": animation_frames,
            "animation_fps": animation_fps,
            "oneshot": oneshot,
        }
        self._animation_resources[id] = config
        return config

    def get_animation_resource(self, id: str) -> dict[str, Any] | None:
        """Retrieves a registered animation resource configuration by ID.

        Args:
            id (str): Unique identifier of the animation resource.

        Returns:
            dict[str, Any] | None: Animation resource payload or None if not registered.
        """
        return self._animation_resources.get(id, None)

    def add_resource(self, category: str, id: str, resource: Any) -> Any:
        """Registers a custom user asset under a specific resource category.

        Args:
            category (str): The resource category name.
            id (str): Unique identifier for the asset.
            resource (Any): The asset object or dictionary to store.

        Returns:
            Any: The stored resource object.
        """
        if category not in self._custom_resources:
            self._custom_resources[category] = {}
        self._custom_resources[category][id] = resource
        return resource

    def get_resource(self, category: str, id: str) -> Any | None:
        """Retrieves a registered custom asset by category and ID.

        Args:
            category (str): The resource category name.
            id (str): Unique identifier for the asset.

        Returns:
            Any | None: The stored resource object or None if not found.
        """
        cat_dict = self._custom_resources.get(category, None)
        if cat_dict is None:
            return None
        return cat_dict.get(id, None)
