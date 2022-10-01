"""
A module to make writing pygame programs easier.
"""

from random import randint

import pygame
from pygame import Vector2

from pygame_engine.input_handler import InputHandler
from pygame_engine.objects import Entity, EntityGroup


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
    on_init(**kwargs):
        Empty method that can be overwritten by a child class to add
        additional attributes and will be called on initialization.
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

    def __init__(self, width: int, height: int, name: str = None, **kwargs):
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
        pygame.init()
        if name:
            pygame.display.set_caption(name)
        self.display = pygame.display.set_mode(
            (width, height), flags=kwargs.get("flags", 0)
        )
        self._clock = pygame.time.Clock()
        self._input = InputHandler()
        self._scenes = {}
        self._active_scene = None
        self._next_scene = None
        self._delta = 0
        self.running = True
        self.fps_max = kwargs.get("fps_max", 60)
        self.on_init(**kwargs)

    def on_init(self, **kwargs):
        """
        Called on instance creation, allows user to define their own attributes.
        """

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
        if self._next_scene is None:
            raise Exception("No scenes have been added to the game")

        scene_transfer_data = None
        while self.running:
            self._active_scene = self._load_scene(self._next_scene)
            self._active_scene.on_load(scene_transfer_data)
            while self._active_scene.running:
                self._quit_check()
                self._input.update(self._active_scene)
                self._active_scene.game_input(self._input)
                self._active_scene.game_process(self._delta)
                self.display.fill((0, 0, 0))
                self._active_scene.render()
                pygame.display.flip()
                self._delta = self._clock.tick(self.fps_max) / 1000
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
        scene_object = scene_class(self)
        return scene_object

    def _quit_check(self):
        """
        Gets events from pygame.event.get() and manages the QUIT event,
        it then passes the event to the handle_event() method.
        """
        if pygame.event.get(pygame.QUIT):
            self.stop()


class Scene:
    """
    Methods
    =======
    on_load():
        Empty method that can be overwritten by a child class to add
        additional attributes and will be called on loading into the
        main game loop
    on_unload():
        Empty method that can be overwritten by a child class to be
        called when the scene is unloaded from the main loop
    on_process():
        Empty method that can be overwritten by a child class. Is called
        once per frame, intended hold all the game logic.
    on_render():
        Empty method that can be overwritten by a child class. Is called
        once per frame, intended to hold all the rendering logic.
    handle_event(event):
        Empty method that can be overwritten by a child class. Is called
        once for every event in pygame.event.get()
    """

    name = "unnamed"

    def __init__(self, root: Application):
        self.camera = Camera()
        self._groups = {}
        self._objects = {}
        self._ui = {}
        self.display = pygame.display.get_surface()
        self.running = True
        self._paused = False
        self.root = root

    def __getitem__(self, key):
        obj = self._objects.get(key, None)
        if obj is None:
            obj = self._groups.get(key, None)
        if obj is None:
            obj = self._ui.get(key, None)
        return obj

    def __iter__(self):
        return iter(self._objects)

    def __len__(self):
        return len(self._objects)

    def keys(self):
        """Returns keys object of _objects attribute."""
        return self._objects.keys()

    def values(self):
        """Returns values object of _objects attribute."""
        return self._objects.values()

    def items(self):
        """Returns items obect of _objects attribute."""
        return self._objects.items()

    def on_load(self, data):
        """
        Empty method that can be overwritten by a child class to add
        additional attributes and will be called on loading into the
        main game loop
        """

    def on_unload(self):
        """
        Empty method that can be overwritten by a child class to be
        called when the scene is unloaded from the main loop
        """

    def input(self, INPUT):
        """
        Empty method that can be overwritten by a child class. Is called once
        per frame, meant to handle game input.

        Args:
            INPUT (InputHandler): InputHandler passed from the main game instance.
        """

    def process(self, delta):
        """
        Empty method that can be overwritten by a child class. Is called
        once per frame, intended hold all the game logic.
        """

    def render(self):
        """
        Method that can be overwritten by a child class. Is called once
        per frame and renders all game objects to the screen.
        """
        self.camera.render()

    def add_object(self, name: str, obj):
        """
        Add an object to the scene, give it a name, and add it to the camera.

        Args:
            name (str): The name to retrieve the object at a later point.
            obj (object): The Object to be added to the scene.
        """
        if name not in self.keys():
            obj.scene = self
            obj.root = self.root
            self._objects[name] = obj
            self.camera.add(obj)
        else:
            print("name already exists")
            obj.kill()

    def remove_object(self, name=None, obj_=None):
        """
        Remove an object from the scene either with the name or a reference to the object.

        Args:
            name (str, optional): The name of the object to remove. Defaults to None.
            obj_ (object, optional): The object to remove. Defaults to None.
        """
        if name and obj_ is None:
            obj = self._objects.pop(name, None)
        elif obj_ and name is None:
            obj = self._objects.pop(obj_.name, None)
        elif obj_ is None and name is None:
            print("Must call function with a name or an object reference")

        if obj:
            self.camera.remove(obj)
            obj.kill()

    def add_group(self, name: str, group: EntityGroup):
        """
        Add a group to the scene, as well as any items in the group.

        Args:
            name (str): The name of the group being added.
            group (EntityGroup): The group being added.
        """
        if name not in self._groups:
            self._groups[name] = group
            if len(group) > 0:
                counter = 1
                for obj in group:
                    obj_name = getattr(obj, "name", "")
                    obj_name = f"{name}_{counter}_{obj_name}"
                    self.add_object(obj_name, obj)
                    counter += 1
        else:
            print("Name already exists")

    def remove_group(self, name: str):
        """
        Remove a group from the scene as well as any objects only in that group.

        Args:
            name (str): Name of the group to remove.
        """
        group = self._groups.pop(name, None)
        if group is None:
            print(f"Group not found : {name}")
        else:
            for obj in group:
                self.remove_object(obj_=obj)

    def add_ui(self, name: str, obj):
        """
        Add an UI object to the scene, give it a name, and add it to the camera.

        Args:
            name (str): The name to retrieve the object at a later point.
            obj (object): The Object to be added to the scene.
        """
        if name not in self._ui:
            obj.scene = self
            self._ui[name] = obj
            self.camera.add(obj)
        else:
            print("name already exists")

    def remove_ui(self, name=None, obj_=None):
        """
        Remove an UI object from the scene either with the name or a reference to the object.

        Args:
            name (str, optional): The name of the object to remove. Defaults to None.
            obj_ (object, optional): The object to remove. Defaults to None.
        """
        if name and obj_ is None:
            obj = self._ui.pop(name, None)
        elif obj_ and name is None:
            obj = self._ui.pop(obj_.name, None)
        elif obj_ is None and name is None:
            print("Must call function with a name or an object reference")

        if obj:
            self.camera.remove(obj)

    def stop(self):
        """Set the flag for the scene to end after the current frame."""
        self.running = False

    def pause(self):
        """
        Set the flag for the scene to pause, only objects with the
        pause_process flag will process.
        """
        self._paused = True

    def unpause(self):
        """Set the flag for the scene to run normally."""
        self._paused = False

    def game_process(self, delta: float):
        """
        Method called by the Engine every frame, calls the process method
        on all game objects and the scene, and then removes any objects
        flagged for deletion.

        Args:
            delta (float): Time since the last frame in seconds.
        """
        kill_items = []
        # Create copies of the objects and ui dicts for iteration
        objects = list(self._objects.items())
        ui_objects = list(self._ui.items())

        for name, obj in objects:
            if hasattr(obj, "process"):
                if obj.game_process:
                    if self._paused:
                        if obj.pause_process:
                            obj.process(delta)
                    else:
                        obj.process(delta)
            if getattr(obj, "do_kill", False):
                kill_items.append(name)

        for name, obj in ui_objects:
            if hasattr(obj, "process"):
                if obj.game_process:
                    if self._paused:
                        if obj.pause_process:
                            obj.process(delta)
                    else:
                        obj.process(delta)
            if getattr(obj, "do_kill", False):
                kill_items.append(name)
        self.process(delta)
        self.camera.process(delta)

        for obj in kill_items:
            self.remove_object(obj)

    def game_input(self, INPUT: InputHandler):
        """
        Method called by the Engine every frame, calls the input method
        on all game objects and the scene.

        Args:
            INPUT (InputHandler): InputHandler passed from the engine.
        """
        for _name, obj in self._ui.items():
            if hasattr(obj, "input"):
                if obj.game_input:
                    if self._paused:
                        if obj.pause_process:
                            obj.input(INPUT)
                    else:
                        obj.input(INPUT)

        for _name, obj in self._objects.items():
            if hasattr(obj, "input"):
                if obj.game_input:
                    if self._paused:
                        if obj.pause_process:
                            obj.input(INPUT)
                    else:
                        obj.input(INPUT)

        self.input(INPUT)

    @property
    def camera_offset(self):
        return self.camera.offset


class Camera:
    """Class that handles the drawing of objects onto the display."""

    STRICT = 0
    SMOOTH = 1

    def __init__(self):
        self.display = pygame.display.get_surface()
        self._bg_color = (0, 0, 0)
        self._background_layer = []
        self._foreground_layer = []
        self._screen_layer = []
        self.target = None
        self.key = "_z"
        self.follow_type = self.STRICT
        self.offset = Vector2()
        self.shake = Vector2()
        self.magnitude = 0
        self.damping = 0.1
        self.display_center = (
            self.display.get_width() / 2,
            self.display.get_height() / 2,
        )
        self.debug = False

    def process(self, _delta):
        """
        Called every frame to update the offset and shake values

        Args:
            _delta (float): For Engine compatibility. Unused.
        """
        if self.target:
            self.update_offset()
        if self.magnitude > 0.1:
            self.magnitude -= self.magnitude * self.damping
            self.shake = Vector2(
                self.magnitude * randint(-10, 10), self.magnitude * randint(-10, 10)
            )
        else:
            self.shake = Vector2()
            self.magnitude = 0

    def render(self):
        """Called every frame to draw all objects to the display."""
        self.display.fill(self._bg_color)
        for obj in self._background_layer:
            if hasattr(obj, "draw") and getattr(obj, "visible", True):
                obj.draw(self.display, self.offset + self.shake)
        for obj in self._foreground_layer:
            if hasattr(obj, "draw") and getattr(obj, "visible", True):
                obj.draw(self.display, self.offset + self.shake)
        for obj in self._screen_layer:
            if hasattr(obj, "draw") and getattr(obj, "visible", True):
                obj.draw(self.display, self.shake)
        if self.debug:
            for obj in self._background_layer:
                if hasattr(obj, "debug_draw"):
                    obj.debug_draw(self.display, self.offset + self.shake)
            for obj in self._foreground_layer:
                if hasattr(obj, "debug_draw"):
                    obj.debug_draw(self.display, self.offset + self.shake)
            for obj in self._screen_layer:
                if hasattr(obj, "debug_draw"):
                    obj.debug_draw(self.display, self.shake)

    def update_offset(self):
        """Updates the Camera offset to the target."""
        if self.target is None:
            return
        offset_x, offset_y = self.offset
        if isinstance(self.target, Vector2):
            target_x = self.target.x
            target_y = self.target.y
        else:
            target_x, target_y = self.target.pos

        if self.follow_type == self.STRICT:
            offset_x = self.display_center[0] - target_x
            offset_y = self.display_center[1] - target_y
        elif self.follow_type == self.SMOOTH:
            offset_x += (self.display_center[0] - target_x - offset_x) / 5
            offset_y += (self.display_center[1] - target_y - offset_y) / 5

        self.offset.update(offset_x, offset_y)

    def set_offset(self, position=(0, 0)):
        """Sets the camera offset to a specified value

        Args:
            position (tuple, optional): New offset to set the Camera to. Defaults to (0, 0).
        """
        offset_x = self.display_center[0] - position[0]
        offset_y = self.display_center[1] - position[1]
        self.offset.update(offset_x, offset_y)

    def set_target(self, target):
        """
        Sets the target of the Camera, which it will follow.

        Args:
            target (Entity, Vector2): The target to follow.
        """
        if isinstance(target, Vector2):
            self.target = target
        elif isinstance(target, Entity):
            self.target = target
        else:
            print("Target must either be a Vector2 or an Entity")

    def set_bg_color(self, color):
        self._bg_color = color

    def add(self, obj):
        """
        Adds an object to the correct layer based on object engine flags.

        Args:
            obj (object): The object to add.
        """
        if getattr(obj, "screen_layer", False):
            self._screen_layer.append(obj)
            # print(obj, "screen_layer")
        elif getattr(obj, "background_layer", False):
            self._background_layer.append(obj)
            # print(obj, "background_layer")
        else:
            self._foreground_layer.append(obj)
            # print(obj, "foreground_layer")
        self.sort()

    def add_entities(self, objects):
        """
        Adds an list of objects to the Camera.

        Args:
            objects (list[object]): The list of objects to add.
        """
        for obj in objects:
            self.add(obj)

    def remove(self, obj):
        """
        Removes an object from the Camera.

        Args:
            obj (object): The object to remove.
        """
        if obj in self._screen_layer:
            self._screen_layer.remove(obj)
        if obj in self._foreground_layer:
            self._foreground_layer.remove(obj)
        if obj in self._background_layer:
            self._background_layer.remove(obj)

    def add_shake(self, magnitude):
        """
        Adds magnitude to the Camera shake.

        Args:
            magnitude (float): The magnitude of the shake to add.
        """
        self.magnitude = magnitude
        self.shake = Vector2()

    def sort(self, key=None):
        """
        Sorts the layers based on either the Camera key or one provided

        Args:
            key (str, optional): The name of an attribute to use to sort
                each layer. Defaults to None.
        """
        if key is None:
            self._background_layer.sort(key=lambda obj: getattr(obj, self.key, 0))
            self._foreground_layer.sort(key=lambda obj: getattr(obj, self.key, 0))
            self._screen_layer.sort(key=lambda obj: getattr(obj, self.key, 0))
        else:
            self._background_layer.sort(key=lambda obj: getattr(obj, key, 0))
            self._foreground_layer.sort(key=lambda obj: getattr(obj, key, 0))
            self._screen_layer.sort(key=lambda obj: getattr(obj, key, 0))
