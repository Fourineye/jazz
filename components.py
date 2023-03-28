import pygame

from Jazz.baseObject import GameObject
from Jazz.utils import Vec2, load_image


class Sprite(GameObject):
    def __init__(self, name="Sprite", **kwargs):
        super().__init__(name, **kwargs)
        self.asset = kwargs.get("asset", None)
        self.flip_x = kwargs.get("flip_x", False)
        self.flip_y = kwargs.get("flip_y", False)

        if self.asset is None:
            self.source = pygame.Surface((10,10))
        else:
            if isinstance(self.asset, pygame.Surface):
                self.source = self.asset
            else:
                self.source = load_image(self.asset)

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
        surface.blit(self.image, self.draw_pos + Vec2(offset))

    def update_image(self):
        self.image = pygame.transform.flip(self.image, self.flip_x, self.flip_y)
        self.image = pygame.transform.rotate(self.source, -self.rotation)
        self._draw_offset = -Vec2(
            self.image.get_width() / 2, self.image.get_height() / 2
        )

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
            new_source = load_image(new_source)
        self._source = new_source
        if self._facing.angle_to((1, 0)) != 0:
            self.image = pygame.transform.rotate(
                self.source, self._facing.angle_to((1, 0))
            )
        else:
            self.image = self.source.copy()

        self._draw_offset = -Vec2(
            self.image.get_width() / 2, self.image.get_height() / 2
        )
    

class AnimatedSprite(Sprite):
    def __init__(self, name="animated sprite", **kwargs):
        self.animation_frames = kwargs.get("animation_frames", [None])
        for frame, data in enumerate(self.animation_frames): 
            if isinstance(data, str):
                self.animation_frames[frame] = load_image(data)
        self._frame = 0
        self.animation_fps = kwargs.get("animation_fps", 30)
        super().__init__(asset=self.animation_frames[0], **kwargs)

    def _process(self, delta):
        self._frame = (self._frame + delta * self.animation_fps) % len(self.animation_frames)
        self.source = self.animation_frames[int(self._frame)]