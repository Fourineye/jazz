"""Global engine references (Globals) and the settings dictionary (SETTINGS)."""

from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from pygame import Window
    from pygame._sdl2 import Renderer

    from .engine import (
        Application,
        InputHandler,
        Keyboard,
        Mouse,
        ResourceManager,
        Scene,
        SoundManager,
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

    # Set by Application.__init__. They are None until an Application exists,
    # but are typed as always present because the engine only runs after that.
    app: "Application" = cast("Application", None)
    scene: "Scene" = cast("Scene", None)
    input: "InputHandler" = cast("InputHandler", None)
    key: "Keyboard" = cast("Keyboard", None)
    mouse: "Mouse" = cast("Mouse", None)
    display: "Surface" = cast("Surface", None)
    renderer: "Renderer" = cast("Renderer", None)
    window: "Window" = cast("Window", None)
    sound: "SoundManager" = cast("SoundManager", None)
    resource: "ResourceManager" = cast("ResourceManager", None)


SETTINGS: dict[str, dict[str, Any]] = {
    "AUDIO": {"master_volume": 1.0, "music_volume": 1.0, "sound_volume": 1.0}
}
