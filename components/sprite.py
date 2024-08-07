import pygame

from ..engine.base_object import GameObject
from ..global_dict import Globals
from ..utils import Vec2


class Sprite(GameObject):
    def __init__(self, name="Sprite", **kwargs):
        super().__init__(name, **kwargs)
        self.asset = kwargs.get("asset", None)
        self._source = None
        self._flip_x = kwargs.get("flip_x", False)
        self._flip_y = kwargs.get("flip_y", False)
        self._scale = Vec2(kwargs.get("scale", Vec2(1, 1)))
        self._alpha = kwargs.get("alpha", 255)
        self._anchor = [1, 1]

        self._img_updated = False
        if self.source is None:
            if self.asset is None:
                temp_source = pygame.Surface((10, 10))
                temp_source.fill(self._color)
                self.source = temp_source
            else:
                if isinstance(self.asset, pygame.Surface):
                    self.source = self.asset
                else:
                    self.source = Globals.scene.load_resource(self.asset)

        anchor = kwargs.get("anchor", None)
        if anchor is not None:
            self.set_anchor(*anchor)

    def on_load(self):
        ...

    def _draw(self, surface: pygame.Surface, offset=None):
        """
        Method called in the scene render function to draw the Entity on a surface.

        Args:
            surface (pygame.Surface): Surface to draw the Entity on.
            offset (Vec2, optional): Offset to add to pos for the draw
                destination. Defaults to None.
        """
        if offset is None:
            offset = Vec2()
        self.update_image()
        if (
                self.image.get_rect(center=self.pos).colliderect(
                    Globals.scene.camera.screen_rect
                )
        ) or self.screen_space:
            surface.blit(self.image, self.draw_pos + Vec2(offset))

    def update_image(self):
        if not self._img_updated:
            self.image = pygame.transform.flip(self.source, self.flip_x, self.flip_y)
            #self.image = pygame.transform.scale_by(self.image, self.scale)
            self.image = pygame.transform.rotate(self.image, -self.rotation)
            self.image.set_alpha(self.alpha)
            self._set_offset()
            self._img_updated = True

    def _set_offset(self):
        self._draw_offset = -Vec2(
            self.image.get_width() * self._anchor[0] / 2,
            self.image.get_height() * self._anchor[1] / 2,
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
        self._set_offset()

    @property
    def draw_pos(self):
        """Returns the top left of self.image when centered on self.pos"""
        return Vec2(self.pos + self._draw_offset)

    @draw_pos.setter
    def draw_pos(self, new_offset):
        """Set new draw offset"""
        self._draw_offset = Vec2(new_offset)

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, new_source):
        if not isinstance(new_source, pygame.Surface):
            new_source = Globals.scene.load_resource(new_source)
        self._source = new_source
        self._img_updated = False
        self.update_image()

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
            raise Exception()

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
        return pygame.Rect(self.draw_pos, self.image.get_size())