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
        self._styled_textures: dict[tuple, Texture] = {}
        self._sprite_sheets: dict[str, list[Image] | list[Texture]] = {}
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
        keys_to_remove = set([
            k
            for k in self._textures
            if k == sprite_id or k.startswith(f"{sprite_id}:")
        ])
        keys_to_remove |= set([
            k
            for k in self._surfaces
            if k == sprite_id or k.startswith(f"{sprite_id}:")
        ])
        keys_to_remove |= set([
            k
            for k in self._sprite_sheets
            if k == sprite_id or k.startswith(f"{sprite_id}:")
        ])
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
        if id not in self._surfaces.keys():
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
        resource = self._colors.get(color.rgb, None)
        if resource is None:
            colorSwatch = Surface((1, 1))
            colorSwatch.fill(color)
            resource = Texture.from_surface(Globals.renderer, colorSwatch)
            self._colors.setdefault(color.rgb, resource)

        return resource

    def get_styled_texture(
        self,
        size: tuple[int, int] | Vec2,
        color: Color,
        radius: int = 0,
        shadow_offset: tuple[int, int] = (0, 0),
        shadow_color: Color = Color(0, 0, 0, 80),
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
            
        pad_x = abs(shadow_offset[0]) + shadow_blur * 2
        pad_y = abs(shadow_offset[1]) + shadow_blur * 2
        
        canvas_w = w + pad_x * 2
        canvas_h = h + pad_y * 2
        canvas = Surface((canvas_w, canvas_h), pygame.SRCALPHA)
        
        rect_x = pad_x
        rect_y = pad_y
        if shadow_offset[0] < 0:
            rect_x -= shadow_offset[0]
        if shadow_offset[1] < 0:
            rect_y -= shadow_offset[1]
            
        rect = Rect(rect_x, rect_y, w, h)
        
        # 1. Draw shadow first
        if shadow_color.a > 0 and (shadow_offset != (0, 0) or shadow_blur > 0):
            shadow_rect = Rect(rect.x + shadow_offset[0], rect.y + shadow_offset[1], w, h)
            if shadow_blur > 0:
                steps = shadow_blur
                for i in range(steps, 0, -1):
                    alpha = int(shadow_color.a * (1.0 - (i / (steps + 1))))
                    c = Color(shadow_color.r, shadow_color.g, shadow_color.b, alpha)
                    r = shadow_rect.inflate(i * 2, i * 2)
                    pygame.draw.rect(canvas, c, r, border_radius=radius + i)
            else:
                pygame.draw.rect(canvas, shadow_color, shadow_rect, border_radius=radius)
                
        # 2. Draw background
        temp_surf = Surface((w, h), pygame.SRCALPHA)
        
        if style in ["skeuomorphic", "gradient", "glossy"] and h > 1:
            shift = 15 if style == "gradient" else 25
            color_light = Color(
                min(255, color.r + shift),
                min(255, color.g + shift),
                min(255, color.b + shift),
                color.a
            )
            color_dark = Color(
                max(0, color.r - shift),
                max(0, color.g - shift),
                max(0, color.b - shift),
                color.a
            )
            
            for y in range(h):
                ratio = y / (h - 1)
                r = int(color_light.r + (color_dark.r - color_light.r) * ratio)
                g = int(color_light.g + (color_dark.g - color_light.g) * ratio)
                b = int(color_light.b + (color_dark.b - color_light.b) * ratio)
                pygame.draw.line(temp_surf, Color(r, g, b, color.a), (0, y), (w, y))
                
            if style == "skeuomorphic":
                bevel_light = Color(255, 255, 255, 60)
                bevel_dark = Color(0, 0, 0, 80)
                
                pygame.draw.line(temp_surf, bevel_light, (0, 0), (w, 0), 1)
                pygame.draw.line(temp_surf, bevel_light, (0, 0), (0, h), 1)
                pygame.draw.line(temp_surf, bevel_dark, (0, h - 1), (w, h - 1), 1)
                pygame.draw.line(temp_surf, bevel_dark, (w - 1, 0), (w - 1, h), 1)
            elif style == "glossy":
                gloss_h = h // 2
                gloss_surf = Surface((w, gloss_h), pygame.SRCALPHA)
                gloss_surf.fill((255, 255, 255, 25))
                temp_surf.blit(gloss_surf, (0, 0))
                
                pygame.draw.rect(temp_surf, (255, 255, 255, 50), (0, 0, w, h), 1)
        else:
            temp_surf.fill(color)
            
        if radius > 0:
            mask = Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=radius)
            temp_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            
        canvas.blit(temp_surf, (rect.x, rect.y))
        
        # 3. Draw border
        if border_color is not None and border_width > 0:
            pygame.draw.rect(canvas, Color(border_color), rect, border_width, border_radius=radius)
            
        resource = Texture.from_surface(Globals.renderer, canvas)
        self._styled_textures[key] = resource
        return resource

    def make_sprite_sheet(
        self,
        id: str,
        dimensions: Vec2 | tuple[int, int],
        offset: tuple[int, int] | Vec2 = (0, 0),
    ) -> list[Image | Texture]:
        """Loads, slices, and registers a grid-aligned sprite sheet of textures.

        Args:
            id (str): The texture path/id to load and slice.
            dimensions (Vec2 | tuple[int, int]): The width and height of each individual frame cell.
            offset (tuple[int, int] | Vec2, optional): Top-left start padding offset. Defaults to (0, 0).

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
