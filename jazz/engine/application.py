"""Application: the window, renderer, main game loop, and scene switching."""

from collections.abc import KeysView

import pygame
from pygame._sdl2 import Renderer

from ..global_dict import Globals
from ..primatives import Draw
from ..utils import JazzException, Surface, load_ini
from .input_handler import InputHandler
from .resource_manager import ResourceManager
from .scene import Scene
from .sound_manager import SoundManager


class Application:
    """Manages the main game loop, window initialization, and active scenes.

    Only a single instance of Application can exist at a time. The instance is
    released when `run()` returns, so a new Application can be created after the
    previous one has shut down.

    Attributes:
        instance (Application | None): The live Application, or None if there is none.
    """
    instance: "Application | None" = None

    def __init__(
        self,
        width: int,
        height: int,
        name: str = "",
        flags: int = 0,
        fps_max: int = 60,
        vsync: bool = False,
        experimental: bool = False,
    ) -> None:
        """Initializes the Application object and pygame, creates the
        application window

        Args:
            width (int): Width of the window in pixels.
            height (int): Height of the window in pixels.
            name (str, optional): String to be shown on the window. Defaults to "".
            flags (int, optional): Unused flag parameter kept for compatibility. Defaults to 0.
            fps_max (int, optional): Sets the max fps that the window will be limited to. Defaults to 60.
            vsync (bool, optional): Controls if the window will try to use vsync. Defaults to False.
            experimental (bool, optional): Unused experimental parameter kept for compatibility. Defaults to False.

        Raises:
            JazzException: If an Application instance already exists.
        """
        if Application.instance is not None:
            raise JazzException("Application has already been initialized.")

        # Re-initialize in case a previous Application called pygame.quit()
        pygame.init()

        load_ini()

        self._window = pygame.Window(name, (width, height))
        self._renderer = Renderer(self._window, vsync=vsync)
        try:
            self._display = self._window.get_surface()
        except pygame.error:
            # Fallback for systems/backends (like macOS Metal/OpenGL) where
            # window surface support is not available when a renderer is active.
            self._display = Surface((width, height))

        self._clock = pygame.time.Clock()
        self._input = InputHandler()
        self._sound = SoundManager()
        self._resource = ResourceManager(self._renderer)

        self._sound.load_settings()

        self._scenes: dict[str, type[Scene] | Scene] = {}
        self._active_scene: Scene | None = None
        self._next_scene: str = ""
        self._delta: float = 0

        self.max_frame_time: float = 1 / 15
        self.running: bool = True
        self.fps_max: int = fps_max

        Globals.app = self
        Globals.input = self._input
        Globals.key = self._input.key
        Globals.mouse = self._input.mouse
        Globals.window = self._window
        Globals.renderer = self._renderer
        Globals.display = self._display
        Globals.sound = self._sound
        Globals.resource = self._resource

        Draw.init()
        Application.instance = self


    def add_scene(self, scene: type[Scene] | Scene) -> None:
        """Adds a scene class or instance reference to the application.

        Args:
            scene (Type[Scene] | Scene): The scene class or instance to add.
        """
        name: str = scene.name
        self._scenes[name] = scene
        if self._next_scene == "":
            self._next_scene = name

    def set_next_scene(self, scene: str | type[Scene] | Scene) -> None:
        """Sets the active scene for the application.

        Args:
            scene (str | Type[Scene] | Scene): The scene name, class, or instance.

        Raises:
            JazzException: If the scene is not registered and not a Scene instance.
        """
        if isinstance(scene, Scene) or (isinstance(scene, type) and issubclass(scene, Scene)):
            name = scene.name
            self._scenes[name] = scene
        else:
            name = str(scene)

        if name not in self._scenes:
            raise JazzException(f"Could not find scene: {name}")
        self._next_scene = name

    def run(self) -> None:
        """Starts the main game loop of the application.

        Releases `Application.instance` once the loop has shut down.

        Raises:
            JazzException: If no scenes have been added to the application
        """

        # Check that app has scenes before running
        if not self._next_scene:
            raise JazzException("No scenes have been added to the game")

        scene_transfer_data = {}

        # Main app loop
        while self.running:
            # Load next scene
            scene = self._load_scene(self._next_scene)
            self._active_scene = scene
            Globals.scene = scene
            scene.on_load(scene_transfer_data)

            # Main scene loop
            while scene.running:
                # Poll events once; this also handles the window close event
                self._input.update()
                if self._input.quit_requested:
                    self.stop()

                # call hook functions
                scene._game_update(self._delta)

                # render game window
                scene.render()
                self._renderer.present()

                # Control fps and record delta time
                self._delta = self._clock.tick(self.fps_max) / 1000
                self._delta = min(self._delta, self.max_frame_time)

            # Allow for transfer of data between scenes
            scene_transfer_data = scene.on_unload()

        self._window.destroy()
        pygame.quit()
        Application.instance = None

    def stop(self) -> None:
        """Sets the neccessary flags to stop the main game loop"""
        self.running = False
        if self._active_scene is not None:
            self._active_scene.running = False

    def _load_scene(self, name: str) -> Scene:
        """Returns a new or pre-instantiated scene from the _scenes attribute.

        Before a scene class is instantiated, the previous scene's cached resources
        and sounds are cleared. Sounds that are still playing keep playing. A
        pre-instantiated scene keeps the cache as is, because it loaded its
        resources when it was built.

        Args:
            name (str): Name of the scene to retrieve.

        Returns:
            Scene: Active scene instance.

        Raises:
            JazzException: If no scene is registered under the name.
        """
        scene_entry = self._scenes.get(name)
        if isinstance(scene_entry, Scene):
            return scene_entry
        if scene_entry is not None:
            self._resource.clear()
            self._sound.clear_sounds(stop=False)
            return scene_entry()
        raise JazzException(f"Could not load scene: {name}")

    def set_caption(self, text: str) -> None:
        """Sets the caption on the application window

        Args:
            text (str): The text to put in the caption.
        """
        if not isinstance(text, str):
            text = str(text)
        self._window.title = text

    def get_fps(self) -> float:
        """Returns fps as a float

        Returns:
            float: Application fps as a float.
        """
        return self._clock.get_fps()

    def get_scenes(self) -> KeysView[str]:
        """Returns the list of registered scene names.

        Returns:
            dict_keys: The names of the scenes registered to the application.
        """
        return self._scenes.keys()
