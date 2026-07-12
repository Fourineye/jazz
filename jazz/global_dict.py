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
    """Static namespace containing global engine systems and references.

    Attributes:
        app (Application): Reference to the running Application instance.
        scene (Scene): Reference to the active Scene instance.
        input (InputHandler): Global input handler dispatching pygame events.
        key (Keyboard): Handles keyboard input polling and state tracking.
        mouse (Mouse): Handles mouse cursor position and button polling.
        display (Surface): The main Pygame display surface.
        renderer (Renderer): The SDL2 hardware-accelerated renderer.
        window (Window): The window wrapper for Pygame.
        sound (SoundManager): Manages channel volume and music/sound loading.
        resource (ResourceManager): Manages texture, surface, and font assets.
    """

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
