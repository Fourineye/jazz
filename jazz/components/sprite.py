import pygame

from .drawable import DrawableObject
from ..global_dict import Globals
from ..utils import Image, Rect, Surface, Texture, Vec2


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

        self._texture: Texture | Image = None
        self.texture = kwargs.get("texture", "default")

    def render(self, offset: Vec2) -> None:
        """Draws the sprite texture onto the screen/canvas.

        Args:
            offset (Vec2): Viewport rendering offset to apply.
        """
        dest = Rect(
            self.draw_pos + offset, self._size.elementwise() * self._scale
        )
        if isinstance(self._texture, Texture):
            self._texture.draw(
                None,
                dest,
                self.rotation,
                -self._draw_offset,
                self.flip_x,
                self.flip_y,
            )
        else:
            self._texture.flip_x = self.flip_x
            self._texture.flip_y = self.flip_y
            self._texture.angle = -self.rotation
            self._texture.alpha = self._alpha
            self._texture.draw(None, dest)

    def kill(self) -> None:
        """Kills the game object, purges dynamic textures, and removes the sprite from the draw list."""
        super().kill()
        Globals.resource.purge_sprite_textures(self.id)

    @property
    def texture(self):
        """Texture | Image: Gets the active Texture or Image asset."""
        return self._texture

    @texture.setter
    def texture(self, new_texture: str | Texture | Image | Surface) -> None:
        """Sets the texture asset, refreshing dimensions and offsets.

        Args:
            new_texture (str | Texture | Image | Surface): Asset key or source image surface.
        """
        if isinstance(new_texture, str):
            self._texture_key = new_texture
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
