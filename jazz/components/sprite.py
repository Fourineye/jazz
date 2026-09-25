"""Sprite component that draws a single texture."""

import pygame

from ..global_dict import Globals
from ..utils import Image, Rect, Surface, Texture, Vec2
from .drawable import DrawableObject


class Sprite(DrawableObject):
    """Rendering component that manages 2D textures, scaling, offsets, and transparency."""

    def __init__(self, name: str = "Sprite", **kwargs) -> None:
        """Initializes the Sprite component.

        Args:
            name (str, optional): The name of the sprite component. Defaults to "Sprite".
            flip_x (bool, optional): Initial horizontal flip state. Defaults to False.
            flip_y (bool, optional): Initial vertical flip state. Defaults to False.
            scale (Vec2, optional): Initial scaling factor. Defaults to Vec2(1, 1).
            alpha (int, optional): Initial opacity transparency (0 to 255). Defaults to 255.
            texture (str | Texture | Surface, optional): Initial texture asset/ID. Defaults to "default".
            anchor (tuple, optional): Horizontal and vertical alignment values (e.g. ("center", "center")). Defaults to None.
        """
        super().__init__(name, **kwargs)

        self._texture: Texture | Image | str | None = None
        texture_arg = kwargs.get("texture", "default")
        if isinstance(texture_arg, (Texture, Image, Surface)):
            self.texture = texture_arg
        else:
            self._texture = texture_arg

    def render(self, offset: Vec2) -> None:
        """Draws the sprite texture onto the screen/canvas.

        Args:
            offset (Vec2): Viewport rendering offset to apply.
        """
        if self._texture is None or isinstance(self._texture, str):
            return
        dest = Rect(
            self.draw_pos + offset, self._size.elementwise() * self._scale
        )
        self._draw_texture(self._texture, dest, -self._draw_offset)

    def _draw_texture(self, texture: Texture | Image, dest: Rect, origin: Vec2) -> None:
        """Draws a Texture or Image with this sprite's rotation, flips, and alpha.

        Both kinds are drawn the same way: a positive rotation turns clockwise on
        screen, matching `facing` and the colliders, and the sprite pivots on
        `origin`. The texture is shared with other sprites, so its settings are
        applied again on every draw. An opaque texture is switched to alpha
        blending when the sprite is translucent, since the default blend mode
        ignores alpha.

        Args:
            texture (Texture | Image): The asset to draw.
            dest (Rect): Destination rectangle in screen space.
            origin (Vec2): Rotation pivot relative to the top-left of `dest`.
        """
        if self._alpha < 255 and texture.blend_mode == pygame.BLENDMODE_NONE:
            texture.blend_mode = pygame.BLENDMODE_BLEND
        texture.alpha = self._alpha
        # pygame treats a falsy origin as "rotate about the centre", and a zero
        # Vector2 is falsy, so the pivot is passed as a tuple
        pivot = (origin.x, origin.y)
        if isinstance(texture, Texture):
            # pygame-ce accepts float origins; its stub says Iterable[int]
            texture.draw(
                None,
                dest,
                self.rotation,
                pivot,  # pyright: ignore[reportArgumentType]
                self.flip_x,
                self.flip_y,
            )
        else:
            texture.flip_x = self.flip_x
            texture.flip_y = self.flip_y
            texture.angle = self.rotation
            texture.origin = pivot
            texture.draw(None, dest)

    def _on_load(self) -> None:
        """Engine hook. Resolves a deferred texture key before the object's on_load runs."""
        if isinstance(self._texture, str):
            self.texture = self._texture
        super()._on_load()

    def kill(self) -> None:
        """Kills the game object, purges dynamic textures, and removes the sprite from the draw list."""
        super().kill()
        Globals.resource.purge_sprite_textures(self.id)

    @property
    def texture(self) -> Texture | Image | str | None:
        """Texture | Image | str | None: Gets the active Texture or Image asset, a texture key
        not yet resolved (before the sprite is loaded), or None if cleared."""
        return self._texture

    @texture.setter
    def texture(self, new_texture: str | Texture | Image | Surface | None) -> None:
        """Sets the texture asset, refreshing dimensions and offsets.

        Args:
            new_texture (str | Texture | Image | Surface | None): Asset key, source image surface,
                or None to clear the texture (the logical size is kept).
        """
        if new_texture is None:
            self._texture = None
            return
        if not isinstance(new_texture, (Texture, Image, Surface)):
            new_texture = Globals.resource.get_texture(new_texture)
        if not isinstance(new_texture, (Texture, Image)):
            new_texture = Globals.resource.add_texture(
                new_texture, self.id, True
            )

        self._texture = new_texture

        if isinstance(self._texture, Image):
            self._size = Vec2(self._texture.get_rect().size)
        else:
            self._size = Vec2(self._texture.width, self._texture.height)
        self._hardware_offset()


from ..engine.serializer import Serializer

Serializer.register_class(Sprite)
