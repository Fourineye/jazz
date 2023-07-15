from ..baseObject import GameObject
from ..utils import map_range
from .easing import LINEAR


class Tween(GameObject):
    """Tween for animation"""

    def __init__(self, target_object, target_property, target_value, time, **kwargs):
        kwargs.setdefault("name", "Tween")
        super().__init__(**kwargs)
        self.target_object = target_object
        self.target_property = target_property
        self._initial_value = None
        self._delta_value = None
        self.target_value = target_value
        self.a_time = time
        self.time = 0
        self.easing = kwargs.get("easing", LINEAR)
        self.loop = kwargs.get("loop", False)
        self.playing = False
        self.on_end = kwargs.get("on_end", None)
        if kwargs.get("playing", False):
            self.play()

    def update(self, delta: float):
        """
        Method that is automatically called on the engine game_process method.

        Args:
            delta (float): The amount of time that has passed since the last
                           frame in seconds.
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

    def play(self, from_beginning=True):
        """Starts the tween animation

        Args:
            from_beginning (bool, optional): An optional argument that
                determines if the tween starts over from the beginning.
                Defaults to True.
        """
        self.playing = True
        self._initial_value = getattr(self.target_object, self.target_property)
        self._delta_value = self.target_value - self._initial_value
        if from_beginning:
            self.time = 0

    def stop(self):
        """Stops the tween animation"""
        self.playing = False
