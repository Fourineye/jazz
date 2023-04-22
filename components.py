import pygame

from Jazz.baseObject import GameObject
from Jazz.user_interface import DEFAULT_FONT
from Jazz.utils import Vec2, load_image, map_range


class Sprite(GameObject):
    def __init__(self, name="Sprite", **kwargs):
        super().__init__(name, **kwargs)
        self.asset = kwargs.get("asset", None)
        self._source = None
        self.flip_x = kwargs.get("flip_x", False)
        self.flip_y = kwargs.get("flip_y", False)
        self.scale = Vec2(kwargs.get("scale", (1, 1)))

    def _on_load(self):
        if self.source is None:
            if self.asset is None:
                self.source = pygame.Surface((10, 10))
            else:
                if isinstance(self.asset, pygame.Surface):
                    self.source = self.asset
                else:
                    self.source = self.scene.load_resource(self.asset)

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
        self.image = pygame.transform.flip(self.source, self.flip_x, self.flip_y)
        self.image = pygame.transform.scale_by(self.image, self.scale)
        self.image = pygame.transform.rotate(self.image, -self.rotation)
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
            new_source = self.scene.load_resource(new_source)
        self._source = new_source
        self.update_image()


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
        self._frame = (self._frame + delta * self.animation_fps) % len(
            self.animation_frames
        )
        self.source = self.animation_frames[int(self._frame)]


class Label(Sprite):
    def __init__(self, name="label", **kwargs):
        super().__init__(name, **kwargs)
        self.font = kwargs.get("font", DEFAULT_FONT)
        self.text_color = kwargs.get("text_color", (255, 255, 255))

        self.text_content = kwargs.get("text", "")
        self.source = self.font.render(self.text_content, True, self.text_color)

    def set_text(self, text):
        if self.text_content != text:
            self.text_content = text
            self.source = self.font.render(text, True, self.text_color)

    def append_text(self, text):
        self.text_content += text
        self.set_text(self.text_content)


class ProgressBar(Sprite):
    def __init__(self, value, max_value, **kwargs):
        kwargs.setdefault("name", "Progress Bar")
        super().__init__(**kwargs)
        self.size = kwargs.get("size", Vec2(200, 50))
        self.value = value
        self.max_value = max_value
        self.bg_color = kwargs.get("bg_color", (100, 100, 100))
        self.color = kwargs.get("color", (100, 100, 200))
        self.line_color = kwargs.get("line_color", (50, 50, 50))
        self.radius = kwargs.get("radius", 0)
        self.line_width = kwargs.get("line_width", 3)
        self.update_bar()

    def update_bar(self):
        # Draw the background color
        self.source = pygame.Surface(self.size)
        pygame.draw.rect(
            self.source,
            self.bg_color,
            self.source.get_rect(),
            border_radius=self.radius,
        )
        # Draw the bar fill
        if self.value > 0:
            fill_height = self.source.get_height() - self.line_width * 2
            fill_width = map_range(
                self.value,
                0,
                self.max_value,
                0,
                self.source.get_width() - self.line_width * 2,
            )
            fill_rect = pygame.Rect(
                self.line_width, self.line_width, fill_width, fill_height
            )
            pygame.draw.rect(self.source, self.color, fill_rect)
        # Draw the border
        if self.line_width > 0:
            pygame.draw.rect(
                self.source,
                self.line_color,
                self.source.get_rect(),
                self.line_width,
                border_radius=self.radius,
            )

    def update_value(self, value):
        self.value = value
        self.update_bar()

    def update_max_value(self, max_value):
        self.max_value = max_value
        self.update_bar()
