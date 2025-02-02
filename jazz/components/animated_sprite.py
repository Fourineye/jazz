import pygame

from .sprite import Sprite
from ..global_dict import Globals


class AnimatedSprite(Sprite):
    def __init__(self, name="animated sprite", **kwargs):
        super().__init__(**kwargs)
        self.animation_frames = kwargs.get("animation_frames", [None])
        self._sheet = kwargs.get("spritesheet", None)
        self._sprite_dim = kwargs.get("sprite_dim", (0, 0))
        self._sprite_offset = kwargs.get("sprite_offset", (0, 0))
        self._playing = kwargs.get("playing", True)
        self._one_shot = kwargs.get("oneshot", False)
        self._frame = 0
        self.animation_fps = kwargs.get("animation_fps", 30)

    def on_load(self):
        super().on_load()
        if self._sheet is None:
            self._sheet = [self._texture]
        else:
            if isinstance(self._sheet, str):
                self._sheet = Globals.scene.make_sprite_sheet(
                    self._sheet, self._sprite_dim, self._sprite_offset
                )
            else:
                for sprite in self._sheet:
                    if isinstance(sprite, str):
                        if Globals.app.experimental:
                            sprite = Globals.scene.load_resource(sprite, 2)
                        else:
                            sprite = Globals.scene.load_resource(sprite)
                    if not isinstance(sprite, (pygame.Surface, pygame._sdl2.Texture, pygame._sdl2.Image)):
                        raise TypeError(
                            "'spritesheet' must be one of the following:\n-Valid path\n-list containing surfaces or valid paths"
                        )

        if self.animation_frames[0] is None:
            self.animation_frames = [i for i in range(len(self._sheet))]

        self.texture = self._sheet[self.animation_frames[0]]

    def update_animation(self, spritesheet=None, animation_frames=None, fps=None):
        if spritesheet is not None:
            if isinstance(spritesheet, str):
                self._sheet = Globals.scene.make_sprite_sheet(
                    spritesheet, self._sprite_dim, self._sprite_offset
                )
            else:
                self._sheet = spritesheet
                for sprite in self._sheet:
                    if isinstance(sprite, str):
                        sprite = Globals.scene.load_resource(sprite)
                    if not isinstance(sprite, (pygame.Surface, pygame._sdl2.Texture, pygame._sdl2.Image)):
                        raise TypeError(
                            "'spritesheet' must be one of the following:\n-Valid path\n-list containing surfaces or valid paths"
                        )

        if animation_frames is not None:
            for frame in animation_frames:
                if not 0 <= frame < len(self._sheet):
                    raise Exception(f"Frame {frame} out  of bounds")
            self.animation_frames = animation_frames
        else:
            self.animation_frames = [i for i in range(len(self._sheet))]

        if fps is not None:
            self.set_fps(fps)

    def update(self, delta):
        if self._playing:
            self._frame = self._frame + delta * self.animation_fps
            if self._frame >= len(self.animation_frames):
                if self._one_shot:
                    self._frame = len(self.animation_frames) - 1
                    self._playing = False
                else:
                    self._frame %= len(self.animation_frames)
            self.texture = self._sheet[self.animation_frames[int(self._frame)]]

    def play(self, start_over=False):
        self._playing = True
        if start_over:
            self._frame = 0

    def stop(self):
        self._playing = False

    def set_fps(self, fps):
        if fps < 0:
            raise Exception(f"invalid fps {fps}, fps must be greater than 0")
        self.animation_fps = fps
