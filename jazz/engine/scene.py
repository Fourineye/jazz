"""
Scene class

"""

from typing import TYPE_CHECKING, Callable
from dataclasses import dataclass

from .group import Group
from .resource_manager import ResourceManager
from ..camera import Camera
from ..global_dict import Globals
from ..physics import Ray, PhysicsGrid
from ..utils import dist_to, direction_to

if TYPE_CHECKING:
    from .base_object import GameObject
    from ..components import Sprite


@dataclass
class Timer:
    time_left: float
    callback: Callable
    args: tuple[any]
    game_time: bool = True


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

    IMAGE = 0
    SPRITE_SHEET = 1
    TEXTURE = 2

    def __init__(self):
        self.camera = Camera()
        self.resource_manager = ResourceManager()
        self._groups = {}
        self._objects = {}
        self._sprites: list[Sprite] = []
        self._timers: list[Timer] = []
        self._physics_world = {
            0: PhysicsGrid(),
            1: PhysicsGrid(),
            2: PhysicsGrid(),
            3: PhysicsGrid(),
        }

        self._debug = False
        self.running = True
        self._paused = False
        Globals.sound.clear_sounds()

    def on_load(self, data) -> None:
        """
        Empty method that can be overwritten by a child class to add
        additional attributes and will be called on loading into the
        main game loop
        """

    def on_unload(self) -> dict:
        """
        Empty method that can be overwritten by a child class to be
        called when the scene is unloaded from the main loop
        """
        return {}

    def update(self, delta) -> None:
        """
        Empty method that can be overwritten by a child class. Is called
        once per frame, intended hold all the game logic.
        """

    def late_update(self, delta) -> None:
        """
        Empty method that can be overwritten by a child class. Is called
        once per frame, intended hold all the game logic.
        """

    def render(self) -> None:
        """
        Method that can be overwritten by a child class. Is called once
        per frame and renders all game objects to the screen.
        """
        self.camera.render()
        if self._debug:
            self.camera.render_debug()

    # Utility Methods

    def stop(self) -> None:
        """Set the flag for the scene to end after the current frame."""
        self.running = False

    def restart(self) -> None:
        Globals.app.set_next_scene(self.name)
        self.running = False

    def pause(self) -> None:
        """
        Set the flag for the scene to pause, only objects with the
        pause_process flag will process.
        """
        self._paused = True

    def unpause(self) -> None:
        """Set the flag for the scene to run normally."""
        self._paused = False

    def set_timer(
        self, time: float, callback: Callable, args: tuple[any], game_time=True
    ) -> None:
        self._timers.append(Timer(time, callback, args, game_time))

    def get_AABB_collisions(self, physics_object) -> list["GameObject"]:
        collisions = []
        for layer, flag in enumerate(physics_object.collision_layers):
            if flag == "1":
                collisions += self._physics_world[layer].get_AABB_collisions(
                    physics_object
                )
        return collisions

    def physics_raycast(self, start, end, layers="0001", blacklist=None):
        ray_cast = Ray(pos=start, length=dist_to(start, end), layers=layers)
        ray_cast.facing = direction_to(start, end)
        return ray_cast.cast(blacklist)

    def get_layer_collisions(self, collider, layer=0):
        return self._physics_world[layer].get_AABB_collisions(collider)

    def get_font(self, *args, **kwargs):
        return self.resource_manager.get_font(*args, **kwargs)

    def load_resource(self, path, resource_type=IMAGE):
        if resource_type == self.IMAGE:
            return self.resource_manager.get_image(path)
        if resource_type == self.SPRITE_SHEET:
            return self.resource_manager.get_sprite_sheet(path)
        if resource_type == self.TEXTURE:
            return self.resource_manager.get_texture(path)

    def make_sprite_sheet(self, path, dimensions, offset=(0, 0)):
        return self.resource_manager.make_sprite_sheet(path, dimensions, offset)

    # Object Management
    def add_object(self, obj: "GameObject", name=None):
        """
        Add an object to the scene, give it a name, and add it to the camera.

        Args:
            name (str): The name to retrieve the object at a later point.
            obj (object): The Object to be added to the scene.
        """
        if obj.id not in self._objects.keys():
            obj._on_load()
            self._objects[obj.id] = obj
        else:
            print("obj already in scene")

        if name is not None and name not in self.__dict__.keys():
            name = name.split(" ")[0]
            obj.name = name
            self.__dict__.setdefault(name, obj)

    def add_physics_object(self, obj, layers):
        for layer, flag in enumerate(layers):
            if flag == "1":
                self._physics_world[layer].add_object(obj)

    def add_sprite(self, sprite: "Sprite"):
        if sprite not in self._sprites:
            self._sprites.append(sprite)
            self._sprites.sort(key=lambda obj: obj.z, reverse=False)

    def remove_object(self, obj):
        """
        Remove an object from the scene either with the name or a reference to the object.

        Args:
            name (str, optional): The name of the object to remove. Defaults to None.
            obj_ (object, optional): The object to remove. Defaults to None.
        """
        if isinstance(obj, str):
            obj = self._objects.pop(obj, None)
        else:
            obj = self._objects.pop(getattr(obj, "id", None), None)

        if obj:
            self.__dict__.pop(obj.name, None)
            obj.scene = None

    def remove_physics_object(self, obj):
        for layer, grid in self._physics_world.items():
            grid.remove_object(obj)

    def remove_sprite(self, sprite: "Sprite"):
        try:
            self._sprites.remove(sprite)
        except ValueError:
            print(f"Sprite not found: {sprite}")


    def toggle_debug(self):
        self._debug = not self._debug

    # Engine Methods
    def _game_update(self, delta: float):
        """
        Method called by the Engine every frame, calls the process method
        on all game objects and the scene, and then removes any objects
        flagged for deletion.

        Args:
            delta (float): Time since the last frame in seconds.
        """

        for grid in self._physics_world.values():
            grid.build_grid()

        kill_items = set()
        objects = list(self._objects.values())

        for obj in objects:
            if getattr(obj, "do_kill", False):
                kill_items.add(obj)
                continue
            if hasattr(obj, "_update"):
                if obj.game_process:
                    if self._paused:
                        if obj.pause_process:
                            obj._update(delta)
                    else:
                        obj._update(delta)

        # call scene process hook
        self.update(delta)

        # late update
        for obj in objects:
            if getattr(obj, "do_kill", False):
                kill_items.add(obj)
                continue
            if hasattr(obj, "_late_update"):
                if obj.game_process:
                    if self._paused:
                        if obj.pause_process:
                            obj._late_update(delta)
                    else:
                        obj._late_update(delta)

        self.late_update(delta)

        # update camera
        if not self._paused:
            self.camera.update(delta)

        # Process Timers
        for timer in self._timers[::-1]:
            if not timer.game_time or not self._paused:
                timer.time_left -= delta
                if timer.time_left <= 0:
                    # print(self._timers, "\nTimer Expired")
                    timer.callback(*timer.args)
                    self._timers.remove(timer)

        # delete objects queued for deletion
        for obj in kill_items:
            obj.kill()

    # Properties and builtins
    def __getitem__(self, key):
        obj = self._groups.get(key, None)
        return obj

    def __iter__(self):
        return iter(self._objects.values())

    def __len__(self):
        return len(self._objects)

    @property
    def keys(self):
        """Returns keys object of _objects attribute."""
        return self._objects.keys()

    @property
    def objects(self):
        """Returns items obect of _objects attribute."""
        return self._objects.values()

    @property
    def camera_offset(self):
        return self.camera.offset

    @property
    def width(self):
        return Globals.display.get_width()

    @property
    def height(self):
        return Globals.display.get_height()

    @property
    def sprites(self) -> list["Sprite"]:
        return self._sprites.copy()
