import pygame

from ..global_dict import SETTINGS, Globals
from ..utils import load_ini
from .input_handler import InputHandler
from .sound_manager import SoundManager


class Application:
    """
    A base application that handles the basic window creation and run loop
    for a pygame application.

    Attributes
    ==========
    display (pygame.Surface): The main display for the Application window.
    running (bool): The flag that keeps the main loop active.
    fps_max (int): The framerate the application will be limited to.

    Methods
    =======
    add_scene(scene: Scene):
        Adds a reference to a Scene class for later loading.
    set_next_scene(name: str):
        Sets the next scene to be loaded based on the scene name.
    run():
        Holds the main game loop of the application. The loop continues as
        long as the running Attribute is True.
    stop():
        Sets running to False so the Application exits at the end of the current frame.
    """

    def __init__(
        self,
        width: int,
        height: int,
        name: str = None,
        flags=0,
        fps_max=60,
        vsync=False,
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

        load_ini()
        if name:
            pygame.display.set_caption(name)
        self.display = pygame.display.set_mode(
            (width, height), flags=flags, vsync=vsync
        )
        self._clock = pygame.time.Clock()
        self._input = InputHandler()
        self._sound = SoundManager()

        self._sound.load_settings()

        self._scenes = {}
        self._active_scene = None
        self._next_scene = None
        self._delta = 0

        self.max_frame_time = 1 / 15
        self.running = True
        self.fps_max = fps_max
        
        Globals.app = self
        Globals.input = self._input
        Globals.key = self._input.key
        Globals.mouse = self._input.mouse
        Globals.display = self.display
        Globals.sound = self._sound

    def add_scene(self, scene):
        """Adds a scene class reference to the game to be initilaized at
        a later point. Setting the next scene if on is not already set

        Args:
            scene (jazz.Scene): The class to add to the application
        """
        name = scene.name
        self._scenes.update({name: scene})
        if self._next_scene is None:
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
            raise Exception("No scenes have been added to the game")

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
                pygame.display.flip()

                # Control fps and record delta time
                self._delta = self._clock.tick(self.fps_max) / 1000
                self._delta = min(self._delta, self.max_frame_time)

            # Allow for transfer of data between scenes
            scene_transfer_data = self._active_scene.on_unload()

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
        pygame.display.set_caption(text)

    def get_fps(self):
        """Returns fps as a float

        Returns:
            float: Application fps as a float.
        """
        return self._clock.get_fps()
