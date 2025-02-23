import pygame

from ..engine.base_object import GameObject
from ..global_dict import Globals
from ..utils import Vec2, Rect, Surface, Texture, Image


class Sprite(GameObject):
    def __init__(self, name: str = "Sprite", **kwargs):
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

    def on_load(self):
        Globals.scene.add_sprite(self)

    def render(self, offset: Vec2):
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

    def _hardware_offset(self):
        self._draw_offset = -(
            Vec2(
                self._size.x * self._anchor[0] / 2,
                self._size.y * self._anchor[1] / 2,
            ).elementwise()
            * self._scale
        )

    def set_anchor(self, horizontal=None, vertical=None):
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

    def kill(self):
        super().kill()
        Globals.scene.remove_sprite(self)

    @property
    def draw_pos(self):
        """Returns the top left of self.image when centered on self.pos"""
        return Vec2(self.pos + self._draw_offset)

    @draw_pos.setter
    def draw_pos(self, new_offset):
        """Set new draw offset"""
        self._draw_offset = Vec2(new_offset)

    @property
    def texture(self):
        return self._texture

    @texture.setter
    def texture(self, new_texture: str | Texture | Image | Surface):
        if not isinstance(new_texture, (Texture, Image, Surface)):
            new_texture = Globals.resource.get_texture(new_texture)
        if not isinstance(new_texture, (Texture, Image)):
            new_texture = Globals.resource.add_texture(new_texture, self.name)

        self._texture = new_texture

        if isinstance(self._texture, Image):
            self._size = Vec2(self._texture.get_rect().size)
        else:
            self._size = Vec2(self._texture.width, self._texture.height)
        self._hardware_offset()

    @property
    def flip_x(self):
        return self._flip_x

    @flip_x.setter
    def flip_x(self, flip_x):
        self._flip_x = flip_x
        self._img_updated = False

    @property
    def flip_y(self):
        return self._flip_y

    @flip_y.setter
    def flip_y(self, flip_y):
        self._flip_y = flip_y
        self._img_updated = False

    @property
    def scale(self):
        return Vec2(self._scale)

    @scale.setter
    def scale(self, scale):
        self._scale = Vec2(scale)
        self._img_updated = False

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, new_alpha):
        if 0 <= new_alpha <= 255:
            self._alpha = new_alpha
            self._img_updated = False
        else:
            raise Exception("Invalid alpha value")

    @property
    def local_rotation(self):
        return self._rotation

    @local_rotation.setter
    def local_rotation(self, angle):
        self._rotation = angle % 360
        self._img_updated = False

    @property
    def rotation(self):
        if self._parent is not None:
            return self._parent.rotation + self._rotation
        else:
            return self._rotation

    @rotation.setter
    def rotation(self, degrees):
        if self._parent is not None:
            self._rotation = degrees - self._parent.rotation
        else:
            self._rotation = degrees
        self._img_updated = False

    @property
    def rect(self):
        return pygame.Rect(
            self.draw_pos, self._size.elementwise() * self._scale
        )
