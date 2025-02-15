from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygame import Window
    from pygame._sdl2 import Renderer
    from .engine import (
        Application,
        Scene,
        InputHandler,
        Keyboard,
        Mouse,
        SoundManager,
        ResourceManager,
    )
    from .utils import Surface


class Globals:
    app: "Application" = None
    scene: "Scene" = None
    input: "InputHandler" = None
    key: "Keyboard" = None
    mouse: "Mouse" = None
    display: "Surface" = None
    renderer: "Renderer" = None
    window: "Window" = None
    sound: "SoundManager" = None
    resource: "ResourceManager" = None


SETTINGS = {
    "AUDIO": {"master_volume": 1.0, "music_volume": 1.0, "sound_volume": 1.0}
}
