"""
Scene class

"""

from typing import TYPE_CHECKING, Callable, Any, Iterable, Type

from ..camera import Camera
from ..global_dict import Globals
from ..physics import Ray, PhysicsGrid
from ..animation import Timer
from ..utils import (
    dist_to,
    direction_to,
    JazzException,
    Vec2,
)

if TYPE_CHECKING:
    from .base_object import GameObject
    from ..physics._physics_object import PhysicsObject
    from ..components import Sprite


class Scene:
    """The class that encapsulates a game scene in Jazz Engine."""

    name = "unnamed"

    def __init__(self) -> None:
        self.camera = Camera()
        self._objects: dict[str, "GameObject"] = {}
        self._to_kill: set[Type["GameObject"]] = set()
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
        Globals.resource.clear()
        Globals.sound.clear_sounds()

    def on_load(self, data: dict[Any, Any]) -> None:
        """Base method that gets called once when the scene is loaded.
        Data from the previous scene is passed to this function.

        Args:
            data (dict[Any, Any]): Data passed from the previous scene.
        """

    def on_unload(self) -> dict[Any, Any]:
        """Base method that gets called once when the scene is unloaded.
        Passes Data to the next scene. By Default it clears any loaded
        resources.

        Returns:
            dict[Any, Any]: Any data that needs to be passed to the next scene.
        """
        return {}

    def update(self, delta: float) -> None:
        """Base method that can be overwritten. Called once per frame.

        Args:
            delta (float): Time in seconds since the last frame.
        """

    def fixed_update(self, delta: float) -> None:
        """Base method that can be overwritten. Called every fixed update

        Args:
            delta (float): A constant 1/60 delta
        """

    def render(self) -> None:
        """Base method that can be overwritten. Called once per frame,
        calls the camera render method."""
        self.camera.render()
        if self._debug:
            self.camera.render_debug()

    # Utility Methods
    def stop(self) -> None:
        """Set the flag for the scene to end after the current frame."""
        self.running = False

    def restart(self) -> None:
        """Set the flag for the scene to end after the current frame.
        Sets the next scene to be the current scene."""
        Globals.app.set_next_scene(self.name)
        self.running = False

    def pause(self) -> None:
        """Pauses the scene. Only objects that are properly flagged
        will update."""
        self._paused = True

    def unpause(self) -> None:
        """Unpauses the scene."""
        self._paused = False

    def toggle_pause(self) -> None:
        """Toggles the pause state of the current scene"""
        self._paused = not self._paused

    def toggle_debug(self) -> None:
        """Toggles the debug state of the scene, Objects will have their
        positions and rotations rendered
        """
        self._debug = not self._debug

    def create_timer(
        self,
        time: float,
        callback: Callable,
        args: tuple[Any],
        pause_process=False,
        one_shot=True,
    ) -> None:
        """Creates a timer that will call the provided callback function
        when it expires.

        Args:
            time (float): The time in seconds before the timer expires.
            callback (Callable): The callback function to call when the timer
                expires.
            args (tuple[Any]): Arguments to provide to the callback function.
            pause_process (bool, optional): Whether the timer should count
                down when the scene is paused. Defaults to False.
        """
        self.add_object(Timer(time, callback, args, pause_process, one_shot))

    def get_layer_collisions(self, collider, layer=0):
        return self._physics_world[layer].get_AABB_collisions(collider)

    # Object Management
    def add_object(self, obj: "Type[GameObject]") -> "GameObject":
        """Adds an object to the scene.

        Args:
            obj (GameObject): The object to add to the scene.

        Returns:
            GameObject: Returns the object added for chaining

        Raises:
            JazzException: Raises an exception if the object is already in the
        """
        if obj.id not in self._objects:
            obj._on_load()
            self._objects[obj.id] = obj
            return obj
        else:
            raise JazzException(f"{obj.id}:{obj.name} already in the scene")

    # TODO clean this up
    def add_physics_object(self, obj: "PhysicsObject", layers) -> None:
        """Adds an object to the scene's physics layers

        Args:
            obj (PhysicsObject): The object to add to the scene
            layers (_type_): _description_
        """
        for layer, flag in enumerate(layers):
            if flag == "1":
                self._physics_world[layer].add_object(obj)

    def add_sprite(self, sprite: "Sprite") -> None:
        """Adds an object to the draw list.

        Args:
            sprite (Sprite): The object to add.
        """
        if sprite not in self._sprites:
            self._sprites.append(sprite)
            self._sprites.sort(key=lambda obj: obj.z, reverse=False)

    def remove_object(self, obj: "GameObject") -> None:
        """Removes an object from the scene.

        Args:
            obj (GameObject): The object to remove.

        """
        if obj.id in self._objects:
            self._objects.pop(obj.id)

    def remove_physics_object(self, obj: "PhysicsObject") -> None:
        """Removes the object from the scene's physics layers

        Args:
            obj (PhysicsObject): The object to remove
        """
        for layer, grid in self._physics_world.items():
            grid.remove_object(obj)

    def remove_sprite(self, sprite: "Sprite"):
        """Removes an object from the draw list.

        Args:
            sprite (Sprite): The object to remove

        Raises:
            JazzException: Raises an exception if the object is not in the draw list
        """
        try:
            self._sprites.remove(sprite)
        except ValueError:
            # raise JazzException(f"Sprite not found: {sprite.id}:{sprite.name}")
            pass

    def get_AABB_collisions(
        self, physics_object: "PhysicsObject"
    ) -> list["GameObject"]:
        """Gets collisions from the scene using Axis Aligned Bounding Boxes.

        Args:
            physics_object (PhysicsObject): The object to check for collisions against

        Returns:
            list[GameObject]: The list of objects that collide
        """
        collisions = []
        for layer, flag in enumerate(physics_object.collision_layers):
            if flag == "1":
                collisions += self._physics_world[layer].get_AABB_collisions(
                    physics_object
                )
        return collisions

    def physics_raycast(
        self,
        start: Vec2,
        end: Vec2,
        layers="0001",
        blacklist: list["PhysicsObject"] = None,
    ):
        ray_cast = Ray(pos=start, length=dist_to(start, end), layers=layers)
        ray_cast.facing = direction_to(start, end)
        return ray_cast.cast(blacklist)

    # Engine Methods
    def _engine_fixed(self, delta: float) -> None:
        for grid in self._physics_world.values():
            grid.build_grid()

        objects = list(self._objects.values())

        for obj in objects:
            if getattr(obj, "do_kill", False):
                self._to_kill.add(obj)
                continue
            if hasattr(obj, "_engine_fixed"):
                if obj.game_process:
                    if self._paused:
                        if obj.pause_process:
                            obj._engine_fixed(delta)
                    else:
                        obj._engine_fixed(delta)
        
        self.fixed_update(delta)

    def _engine_update(self, delta: float) -> None:
        """Engine Method. Updates the scene
            and deletes objects marked for deletion.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        objects = list(self._objects.values())

        for obj in objects:
            if getattr(obj, "do_kill", False):
                self._to_kill.add(obj)
                continue
            if hasattr(obj, "_engine_update"):
                if obj.game_process:
                    if self._paused:
                        if obj.pause_process:
                            obj._engine_update(delta)
                    else:
                        obj._engine_update(delta)

        # call scene process hook
        self.update(delta)

        # update camera
        if not self._paused:
            self.camera.update(delta)

        # delete objects queued for deletion
        for obj in self._to_kill:
            obj.kill()
        self._to_kill.clear()

    # Properties and builtins
    def __getitem__(self, key):
        obj = self._objects.get(key, None)
        return obj

    def __iter__(self):
        return iter(self._objects.values())

    def __len__(self):
        return len(self._objects)

    @property
    def keys(self) -> Iterable[str]:
        """Returns keys object of _objects attribute."""
        return self._objects.keys()

    @property
    def objects(self) -> Iterable["GameObject"]:
        """Returns items obect of _objects attribute."""
        return self._objects.values()

    @property
    def camera_offset(self) -> Vec2:
        return self.camera.offset

    @property
    def width(self) -> int:
        return Globals.display.get_width()

    @property
    def height(self) -> int:
        return Globals.display.get_height()

    @property
    def sprites(self) -> list["Sprite"]:
        """Returns the list of objects to draw.

        Returns:
            list[Sprite]: List of objects that will get drawn.
        """
        return self._sprites
