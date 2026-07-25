from ..global_dict import Globals
from ..utils import Image, JazzException, Surface, Texture, Vec2
from .sprite import Sprite


class AnimatedSprite(Sprite):
    """Component that renders multi-frame spritesheets with playing controls."""

    def __init__(self, name: str = "animated sprite", **kwargs) -> None:
        """Initializes the AnimatedSprite component.

        Args:
            name (str, optional): The name of the animated sprite object. Defaults to "animated sprite".
            animation_frames (list[int], optional): Sequence indices of frames to play. Defaults to [-1] (plays all).
            spritesheet (str | list, optional): Slices/images source of the frames. Defaults to None.
            sprite_dim (tuple, optional): Dimensions of each frame cell in pixels. Defaults to (0, 0).
            sprite_offset (tuple, optional): Slicing offset in pixels. Defaults to (0, 0).
            playing (bool, optional): Auto-start playback flag. Defaults to True.
            oneshot (bool, optional): Loop disable flag. Defaults to False.
            animation_fps (int, optional): Playback frame rate. Defaults to 30.
        """
        super().__init__(**kwargs)
        self.animation_frames: list[int] = kwargs.get("animation_frames", [-1])
        self._sprite_dim: Vec2 = Vec2(kwargs.get("sprite_dim", (0, 0)))
        self._sprite_offset: Vec2 = Vec2(kwargs.get("sprite_offset", (0, 0)))
        self._playing: bool = kwargs.get("playing", True)
        self._one_shot: bool = kwargs.get("oneshot", False)
        self._frame: float = 0
        self.animation_fps: int = kwargs.get("animation_fps", 30)

        spritesheet_arg: str | list[str | Texture | Image | Surface] | None = kwargs.get("spritesheet", None)
        if spritesheet_arg is None:
            self._sheet: list[Image | Texture] = [self._texture]
        else:
            self._sheet = self._parse_spritesheet(spritesheet_arg)

        if self.animation_frames[0] == -1:
            self.animation_frames = [i for i in range(len(self._sheet))]

        self.texture = self._sheet[self.animation_frames[0]]

    def _parse_spritesheet(
        self,
        spritesheet: str | list[str | Texture | Image | Surface],
    ) -> list[Image | Texture]:
        """Parses a spritesheet source argument into a list of textures or images.

        Args:
            spritesheet (str | list): File path to spritesheet or list of frame sources.

        Returns:
            list[Image | Texture]: Parsed list of texture/image frame assets.

        Raises:
            TypeError: If an element in spritesheet list is of an invalid type.
        """
        if isinstance(spritesheet, str):
            try:
                return Globals.resource.get_sprite_sheet(spritesheet)
            except JazzException:
                return Globals.resource.make_sprite_sheet(
                    spritesheet, self._sprite_dim, self._sprite_offset
                )

        parsed_sheet: list[Image | Texture] = []
        for i, item in enumerate(spritesheet):
            sprite: Texture | Image | Surface | str = item
            if isinstance(sprite, str):
                sprite = Globals.resource.get_texture(sprite)
            elif isinstance(sprite, Surface):
                sprite = Globals.resource.add_texture(
                    sprite, f"{self.id}:{i}", True
                )
            if not isinstance(sprite, (Texture, Image)):
                raise TypeError(
                    "'spritesheet' must be one of the following:\n"
                    "-Valid path\n"
                    "-list containing surfaces or valid paths"
                )
            parsed_sheet.append(sprite)
        return parsed_sheet

    def update_animation(
        self,
        spritesheet: str | list[str | Texture | Image | Surface] | None = None,
        animation_frames: list[int] | None = None,
        fps: int | None = None,
    ) -> None:
        """Updates animation settings dynamically.

        Args:
            spritesheet (str | list, optional): Slices/images source of the frames. Defaults to None.
            animation_frames (list[int], optional): Sequence indices of frames to play. Defaults to None.
            fps (int, optional): Playback frame rate. Defaults to None.
        """
        if spritesheet is not None:
            self._sheet = self._parse_spritesheet(spritesheet)

        if animation_frames is not None:
            for frame in animation_frames:
                if not 0 <= frame < len(self._sheet):
                    raise Exception(f"Frame {frame} out  of bounds")
            self.animation_frames = animation_frames
        else:
            self.animation_frames = [i for i in range(len(self._sheet))]

        if fps is not None:
            self.set_fps(fps)

    def update(self, delta: float) -> None:
        """Advances active frame index based on delta time and playback FPS.

        Args:
            delta (float): Time since the last frame in seconds.
        """
        if self._playing:
            old_idx = int(self._frame)
            self._frame = self._frame + delta * self.animation_fps
            if self._frame >= len(self.animation_frames):
                if self._one_shot:
                    self._frame = len(self.animation_frames) - 1
                    self._playing = False
                else:
                    self._frame %= len(self.animation_frames)
            new_idx = int(self._frame)
            if new_idx != old_idx or self._texture is not self._sheet[self.animation_frames[new_idx]]:
                self.texture = self._sheet[self.animation_frames[new_idx]]

    def play(self, start_over: bool = False) -> None:
        """Starts or resumes animation playback.

        Args:
            start_over (bool, optional): Rewind frame tracker to 0. Defaults to False.
        """
        self._playing = True
        if start_over:
            self._frame = 0

    def stop(self) -> None:
        """Stops/pauses animation playback."""
        self._playing = False

    def set_fps(self, fps: int) -> None:
        """Sets the animation playback FPS rate.

        Args:
            fps (int): Frame rate value.
        """
        if fps < 0:
            raise Exception(f"invalid fps {fps}, fps must be greater than 0")
        self.animation_fps = fps
