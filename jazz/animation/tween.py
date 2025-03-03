from typing import Any, Callable

from .easing import LINEAR
from ..engine.base_object import GameObject
from ..utils import map_range


class Tween(GameObject):
    """Tween for animation"""

    def __init__(
        self,
        target_object: GameObject,
        target_property: str,
        target_value: Any,
        time: float,
        **kwargs,
    ):
        """A an object that moves a property between two numeric values using a given easing function.

        Args:
            target_object (GameObject): The object whose property is being tweened
            target_property (str): The string representation of the property being changed
            target_value (Any): The value to tween to.
            time (float): The time in seconds for the tween to take
            easing (Callable, optional): The easing function to use, takes in a number between 0 - 1 and returns a float. Default is LINEAR
            on_end (Callable, optional): A function that will be called when the tween is complete. Default is None
            play (bool, optional): If this is true the tween will start when it is created. Default is False
        """
        kwargs.setdefault("name", "Tween")
        super().__init__(**kwargs)
        self.target_object = target_object
        self.target_property = target_property
        self._initial_value = None
        self._delta_value = None
        self.target_value = target_value
        self.a_time = time
        self.time = 0
        self.easing: Callable[[float], float] = kwargs.get("easing", LINEAR)
        self.loop = kwargs.get("loop", False)
        self.playing = False
        self.on_end: Callable[[]] = kwargs.get("on_end", None)
        if kwargs.get("play", False):
            self.play()

    def _implementation_update(self, delta: float) -> None:
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
        time_factor = map_range(self.time, 0, self.a_time, 0, 1)
        delta_factor = self.easing(time_factor)

        setattr(
            self.target_object,
            self.target_property,
            self._initial_value + self._delta_value * delta_factor,
        )

        if self.time >= self.a_time:
            self.time = 0
            if not self.loop:
                self.playing = False
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
