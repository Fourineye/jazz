"""Tween: animates a property of a GameObject toward a target value over time."""

from collections.abc import Callable
from typing import Any

from ..engine.base_object import BaseObject, GameObject
from ..global_dict import Globals
from ..utils import JazzException, map_range
from .easing import LINEAR


class Tween(GameObject):
    """Animates one property of a target object toward a value with an easing function.

    Attributes:
        target_object (GameObject | None): The object being animated, or None
            until a named or parent target has been found.
        target_property (str): Name of the attribute that is set each frame.
        target_value (Any): The value the property ends at.
        a_time (float): Duration of one run of the tween, in seconds.
        time (float): Time elapsed in the current run, in seconds.
        playing (bool): Whether the tween is running.
    """

    def __init__(
        self,
        target_object: GameObject | str | None = None,
        target_property: str = "pos",
        target_value: Any = 0,
        time: float = 1.0,
        **kwargs,
    ) -> None:
        """An object that moves a property between two numeric values using a given easing function.

        Args:
            target_object (GameObject | str | None, optional): The object whose property is
                tweened, or the name or id of a scene object, looked up when the tween is
                added to the scene. None tweens the tween's parent. Defaults to None.
            target_property (str): The string representation of the property being changed
            target_value (Any): The value to tween to.
            time (float): The time in seconds for the tween to take
            easing (Callable, optional): The easing function to use, takes in a number between 0 - 1 and returns a float. Default is LINEAR
            loop (bool, optional): If True, the tween loops continuously. Defaults to False.
            one_shot (bool, optional): If True, marks the tween object for deletion when completed. Defaults to True.
            on_end (Callable, optional): A function that will be called when the tween is complete. Default is None
            play (bool, optional): If this is true the tween will start when it is created, or
                once its target is found if the target is a name or the parent. Default is False
        """
        if isinstance(target_object, str):
            kwargs["target_object"] = target_object
        elif isinstance(target_object, GameObject):
            # Saved by name so a serialized tween can find its target again
            kwargs["target_object"] = target_object.name
        kwargs["target_property"] = target_property
        kwargs["target_value"] = target_value
        kwargs["time"] = time
        kwargs.setdefault("name", "Tween")
        super().__init__(**kwargs)
        self._target_ref: GameObject | str | None = target_object
        self.target_object: GameObject | None = (
            target_object if isinstance(target_object, GameObject) else None
        )
        self.target_property: str = target_property
        self._initial_value: Any = None
        self._delta_value: Any = None
        self.target_value: Any = target_value
        self.a_time: float = time
        self.time: float = 0.0
        self.easing: Callable[[float], float] = kwargs.get("easing", LINEAR)
        self.loop: bool = kwargs.get("loop", False)
        self.one_shot: bool = kwargs.get("one_shot", True)
        self.playing: bool = False
        self.on_end: Callable[[], Any] | None = kwargs.get("on_end", None)
        self._play_on_load: bool = False
        if kwargs.get("play", False):
            if self.target_object is not None:
                self.play()
            else:
                self._play_on_load = True

    def _resolve_target(self) -> GameObject | None:
        """Finds the target object from the name, id, or parent given at construction.

        Returns:
            GameObject | None: The target, or None if it cannot be found yet.
        """
        ref = self._target_ref
        if isinstance(ref, GameObject):
            return ref
        if ref is None:
            parent = self._parent
            return parent if isinstance(parent, GameObject) else None
        if Globals.scene is None:
            return None
        pending: list[BaseObject] = list(Globals.scene.objects)
        while pending:
            obj = pending.pop()
            if isinstance(obj, GameObject) and ref in (obj.id, obj.name):
                return obj
            pending.extend(obj._children.values())
        return None

    def _on_load(self) -> None:
        """Engine hook. Resolves a named or parent target and starts a pending `play`."""
        if self.target_object is None:
            self.target_object = self._resolve_target()
        if self._play_on_load and self.target_object is not None:
            self._play_on_load = False
            self.play()
        super()._on_load()

    def update(self, delta: float) -> None:
        """Method that updates the tween and applys the easing to the target
            object and property.

        Args:
            delta (float): Time in seconds since the last frame

        Raises:
            JazzException: If `play` was requested but the target still cannot be found.
        """
        if self._play_on_load:
            # The target may have been added to the scene after the tween
            self._play_on_load = False
            self.play()

        if not self.playing or self.target_object is None:
            return

        if self.time >= self.a_time:
            if self.loop:
                self.time -= self.a_time
            else:
                self.time = self.a_time
        time_factor = map_range(self.time, 0.0, self.a_time, 0.0, 1.0)
        delta_factor = self.easing(time_factor)

        setattr(
            self.target_object,
            self.target_property,
            self._initial_value + self._delta_value * delta_factor,
        )

        if self.time >= self.a_time:
            self.time = 0.0
            if not self.loop:
                self.playing = False
                if self.one_shot:
                    self._kill = True
            if callable(self.on_end):
                self.on_end()
        self.time += delta

    def play(self, from_beginning: bool = True) -> None:
        """Starts the tween animation

        Args:
            from_beginning (bool, optional): Determines if the tween starts
                over from the beginning. Defaults to True.

        Raises:
            JazzException: If the tween has no target object.
        """
        if self.target_object is None:
            self.target_object = self._resolve_target()
        if self.target_object is None:
            raise JazzException(
                f"Tween '{self.name}' has no target object: {self._target_ref!r} was not found"
            )
        self.playing = True
        self._initial_value = getattr(self.target_object, self.target_property)
        self._delta_value = self.target_value - self._initial_value
        if from_beginning:
            self.time = 0

    def stop(self) -> None:
        """Stops the tween animation"""
        self.playing = False

from ..engine.serializer import Serializer

Serializer.register_class(Tween)
