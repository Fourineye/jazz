from typing import Any, Callable

from .easing import LINEAR
from ..engine.base_object import GameObject
from ..utils import map_range


class Tween(GameObject):
    """Tween for animation"""

    def __init__(
        self,
        target_object: GameObject = None,
        target_property: str = "pos",
        target_value: Any = 0,
        time: float = 1.0,
        **kwargs,
    ) -> None:
        """An object that moves a property between two numeric values using a given easing function.

        Args:
            target_object (GameObject): The object whose property is being tweened
            target_property (str): The string representation of the property being changed
            target_value (Any): The value to tween to.
            time (float): The time in seconds for the tween to take
            easing (Callable, optional): The easing function to use, takes in a number between 0 - 1 and returns a float. Default is LINEAR
            loop (bool, optional): If True, the tween loops continuously. Defaults to False.
            one_shot (bool, optional): If True, marks the tween object for deletion when completed. Defaults to True.
            on_end (Callable, optional): A function that will be called when the tween is complete. Default is None
            play (bool, optional): If this is true the tween will start when it is created. Default is False
        """
        kwargs["target_property"] = target_property
        kwargs["target_value"] = target_value
        kwargs["time"] = time
        kwargs.setdefault("name", "Tween")
        super().__init__(**kwargs)
        self.target_object: GameObject = target_object
        self.target_property: str = target_property
        self._initial_value: float | None = None
        self._delta_value: float | None = None
        self.target_value: float = target_value
        self.a_time: float = time
        self.time: float = 0.0
        self.easing: Callable[[float], float] = kwargs.get("easing", LINEAR)
        self.loop: bool = kwargs.get("loop", False)
        self.one_shot: bool = kwargs.get("one_shot", True)
        self.playing: bool = False
        self.on_end: Callable[[]] = kwargs.get("on_end", None)
        if kwargs.get("play", False):
            self.play()

    def update(self, delta: float) -> None:
        """Method that updates the tween and applys the easing to the target
            object and property.

        Args:
            delta (float): Time in seconds since the last frame
        """
        if not self.playing:
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
                    self.do_kill = True
            if callable(self.on_end):
                self.on_end()
        self.time += delta

    def play(self, from_beginning: bool = True) -> None:
        """Starts the tween animation

        Args:
            from_beginning (bool, optional): Determines if the tween starts
                over from the beginning. Defaults to True.
        """
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
