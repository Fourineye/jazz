import pygame

from ..engine.base_object import GameObject
from ..global_dict import Globals
from ..utils import Vec2, Rect, Surface, Texture, Image


class Sprite(GameObject):
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
        self._flip_x: bool = kwargs.get("flip_x", False)
        self._flip_y: bool = kwargs.get("flip_y", False)
        self._scale: Vec2 = Vec2(kwargs.get("scale", Vec2(1, 1)))
        self._alpha: int = kwargs.get("alpha", 255)
        self._anchor: list[int] = [1, 1]

        self._texture: Texture | Image = None
        self.texture = kwargs.get("texture", "default")

        anchor: list[int] | None = kwargs.get("anchor", None)
        if anchor is not None:
            self.set_anchor(*anchor)

    def on_load(self) -> None:
        """Registers the sprite to the active scene's draw list on mount."""
        Globals.scene.add_sprite(self)

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

    def _hardware_offset(self) -> None:
        """Recalculates hardware draw offsets based on the anchor point alignment and scale."""
        self._draw_offset = -(
            Vec2(
                self._size.x * self._anchor[0] / 2,
                self._size.y * self._anchor[1] / 2,
            ).elementwise()
            * self._scale
        )

    def set_anchor(self, horizontal: str | int | None = None, vertical: str | int | None = None) -> None:
        """Configures the anchor point alignment.

        Args:
            horizontal (str | int, optional): Left (0), center (1), or right (2) horizontal anchor alignment.
            vertical (str | int, optional): Top (0), center (1), or bottom (2) vertical anchor alignment.
        """
        if vertical in ["top", 0]:
            self._anchor[1] = 0
        elif vertical in ["center", 1]:
            self._anchor[1] = 1
        elif vertical in ["bottom", 2]:
            self._anchor[1] = 2
        if horizontal in ["left", 0]:
            self._anchor[0] = 0
        elif horizontal in ["center", 1]:
            self._anchor[0] = 1
        elif horizontal in ["right", 2]:
            self._anchor[0] = 2
        self._hardware_offset()

    def kill(self) -> None:
        """Kills the game object, purges dynamic textures, and removes the sprite from the draw list."""
        super().kill()
        Globals.resource.purge_sprite_textures(self.id)
        Globals.scene.remove_sprite(self)

    @property
    def draw_pos(self):
        """Vec2: Gets the top-left drawing position coordinate relative to the camera."""
        return Vec2(self.pos + self._draw_offset)

    @draw_pos.setter
    def draw_pos(self, new_offset: Vec2 | tuple[float, float]) -> None:
        """Sets a manual draw offset offset.

        Args:
            new_offset (Vec2 | tuple): The new drawing offset.
        """
        self._draw_offset = Vec2(new_offset)

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

    @property
    def flip_x(self):
        """bool: Horizontal flip status."""
        return self._flip_x

    @flip_x.setter
    def flip_x(self, flip_x: bool) -> None:
        self._flip_x = flip_x
        self._img_updated = False

    @property
    def flip_y(self):
        """bool: Vertical flip status."""
        return self._flip_y

    @flip_y.setter
    def flip_y(self, flip_y: bool) -> None:
        self._flip_y = flip_y
        self._img_updated = False

    @property
    def scale(self):
        """Vec2: Scaling factor of the sprite."""
        return Vec2(self._scale)

    @scale.setter
    def scale(self, scale: Vec2 | tuple[float, float]) -> None:
        self._scale = Vec2(scale)
        self._img_updated = False

    @property
    def alpha(self):
        """int: Opacity level between 0 (fully transparent) and 255 (fully opaque)."""
        return self._alpha

    @alpha.setter
    def alpha(self, new_alpha: int) -> None:
        if 0 <= new_alpha <= 255:
            self._alpha = new_alpha
            self._img_updated = False
        else:
            raise Exception("Invalid alpha value")

    def on_transform_change(self) -> None:
        """Clears rendering cache triggers on coordinate updates."""
        self._img_updated = False

    @property
    def rect(self):
        """Rect: Gets the bounding rectangle of the sprite in screen/world space."""
        return pygame.Rect(
            self.draw_pos, self._size.elementwise() * self._scale
        )
