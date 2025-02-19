from typing import Type

import pygame

from .input_handler import InputHandler
from .scene import Scene
from .sound_manager import SoundManager
from .resource_manager import ResourceManager
from ..global_dict import Globals
from ..utils import load_ini, JazzException
from ..primatives import Draw


class Application:
    instance: "Application" = None
    """
    A class that handles the basic window creation and run loop
    for a pygame application.
    """

    def __init__(
        self,
        width: int,
        height: int,
        name: str = "",
        flags=0,
        fps_max=60,
        vsync=False,
        experimental=False,
    ):
        """Initializes the Application object and pygame, creates the
        application window

        Args:
            width (int): Width of the window in pixels
            height (int): Height of the window in pixels
            name (str, optional): String to be shown on the window. Defaults to None.
            flags (int, optional): Flags to be passed to the pygame.display.set_mode function. Defaults to 0.
            fps_max (int, optional): Sets the max fps that the window will be limited to. Defaults to 60.
            vsync (bool, optional): Controls if the window will try to use vsync. Defaults to False.
        """
        if self.instance is not None:
            raise JazzException("Application has already been initialized.")

        load_ini()
        self.experimental: bool = experimental

        self._window = pygame.Window(name, (width, height))
        self._renderer = pygame._sdl2.Renderer(self._window, vsync=vsync)
        self._display = self._window.get_surface()

        self._clock = pygame.time.Clock()
        self._input = InputHandler()
        self._sound = SoundManager()
        self._resource = ResourceManager(self._renderer)

        self._sound.load_settings()

        self._scenes: dict[str, Type[Scene]] = {}
        self._active_scene: str = ""
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

        if self.experimental:
            self._screen_refresh = self._renderer.present
        else:
            self._screen_refresh = self._window.flip

    def add_scene(self, scene: Type[Scene]):
        """Adds a scene class reference to the game to be initilaized at
        a later point. Setting the next scene if on is not already set

        Args:
            scene (jazz.Scene): The class to add to the application
        """
        name: str = scene.name
        self._scenes[name] = scene
        if self._next_scene == "":
            self._next_scene = name

    def set_next_scene(self, name: str):
        """Sets the _next_scene property verifying that the scene exists in
        the game first

        Args:
            name (str): The name of a given Scene added to the application

        Raises:
            Exception: The given string does not match the name of any added Scenes
        """
        scene_class = self._scenes.get(name)
        if scene_class is None:
            raise Exception(f"Could not find scene: {name}")
        self._next_scene = name

    def run(self):
        """Starts the main game loop of the application.

        Raises:
            Exception: If no scenes have been added to the application
        """

        # Check that app has scenes before running
        if self._next_scene is None:
            raise JazzException("No scenes have been added to the game")

        scene_transfer_data = {}

        # Main app loop
        while self.running:
            # Load next scene
            self._active_scene = self._load_scene(self._next_scene)
            Globals.scene = self._active_scene
            self._active_scene.on_load(scene_transfer_data)

            # Main scene loop
            while self._active_scene.running:
                # Handle window events
                self._quit_check()

                # call hook functions
                self._input.update()
                self._active_scene._game_update(self._delta)

                # render game window
                self._active_scene.render()
                self._screen_refresh()

                # Control fps and record delta time
                self._delta = self._clock.tick(self.fps_max) / 1000
                self._delta = min(self._delta, self.max_frame_time)

            # Allow for transfer of data between scenes
            scene_transfer_data = self._active_scene.on_unload()

        self._window.destroy()
        pygame.quit()

    def stop(self):
        """Sets the neccessary flags to stop the main game loop"""
        self.running = False
        if self._active_scene is not None:
            self._active_scene.running = False

    def _load_scene(self, name):
        """
        Returns a new instance of a scene in the _scenes attribute.

        Args:
            name (string): Name of the scene class to retrieve.

        Returns:
            Scene: New instance of the scene class.
        """
        scene_class = self._scenes.get(name)
        scene_object = scene_class()
        return scene_object

    def _quit_check(self):
        """
        Gets events from pygame.event.get() and manages the QUIT event,
        it then passes the event to the handle_event() method.
        """
        if pygame.event.get(pygame.QUIT):
            self.stop()

    def set_caption(self, text: str):
        """Sets the caption on the application window

        Args:
            text (str): The text to put in the caption.
        """
        if not isinstance(text, str):
            text = str(text)
        self._window.title = text

    def get_fps(self):
        """Returns fps as a float

        Returns:
            float: Application fps as a float.
        """
        return self._clock.get_fps()

    def get_scenes(self):
        return self._scenes.keys()
