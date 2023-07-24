import pygame

from ..global_dict import SETTINGS, Game_Globals
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
        """
        Initializes the Application object and pygame, creates the
        application window

        Args:
        =====
            width (int): Pixel width of the window.
            height (int): Pixel Height of the window.
            name (str, optional): Name to be displayed at the top of the window.
                Defaults to None.

        Kwargs:
        ======
            fps_max (int): The max frame rate the application will run.
                Defaults to 60.
            flags (int): Flags from pygame to be passed to the display on creation.
                Defaults to 0.
            **kwargs (dict): Remaining kwargs will be passed on to the on_init method.
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

        Game_Globals["App"] = self
        Game_Globals["Input"] = self._input
        Game_Globals["Key"] = self._input.key
        Game_Globals["Mouse"] = self._input.mouse
        Game_Globals["Display"] = self.display
        Game_Globals["Sound"] = self._sound

    def add_scene(self, scene):
        """
        Adds a scene class reference to the game to be initilaized at
        a later point. Setting the next scene if on is not already set
        """
        name = scene.name
        self._scenes.update({name: scene})
        if self._next_scene is None:
            self._next_scene = name

    def set_next_scene(self, name):
        """
        Sets the _next_scene property verifying that the scene exists in
        the game first
        """
        scene_class = self._scenes.get(name)
        if scene_class is None:
            raise Exception(f"Could not find scene: {name}")
        self._next_scene = name

    def run(self):
        """
        Holds the main game loop of the application. The loop continues as
        long as the running Attribute is True.
        """

        # Check that app has scenes before running
        if self._next_scene is None:
            raise Exception("No scenes have been added to the game")

        scene_transfer_data = {}

        # Main app loop
        while self.running:
            # Load next scene
            self._active_scene = self._load_scene(self._next_scene)
            Game_Globals["Scene"] = self._active_scene
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
        """Sets the running flags to false"""
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
        if not isinstance(text, str):
            text = str(text)
        pygame.display.set_caption(text)

    def get_fps(self):
        return self._clock.get_fps()
