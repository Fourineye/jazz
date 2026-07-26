from typing import Callable, Any
import uuid

from ..global_dict import Globals


class Timer:
    """A countdown timer that triggers a callback when it expires."""

    def __init__(
        self,
        time_left: float,
        callback: Callable[..., Any] | str,
        args: tuple[Any, ...] = (),
        pause_process: bool = False,
        one_shot: bool = True,
    ) -> None:
        """Initializes the Timer.

        Args:
            time_left (float): Countdown duration in seconds.
            callback (Callable[..., Any] | str): The function to call when the timer expires.
            args (tuple[Any, ...], optional): Arguments to pass to the callback. Defaults to empty tuple.
            pause_process (bool, optional): If True, timer will pause counting down when scene is paused. Defaults to False.
            one_shot (bool, optional): If True, the timer kills itself after firing once. Defaults to True.
        """
        self.id = str(uuid.uuid1())
        self.time = time_left
        self.time_left = time_left
        callback_arg = callback
        if isinstance(callback, str):
            from ..engine.serializer import Serializer
            callback = Serializer.resolve_script(callback)
        self.callback = callback
        self.args = args
        self.game_process = True
        self.pause_process = pause_process
        self.one_shot = one_shot
        self.do_kill = False
        self._kwargs = {"time_left": time_left, "callback": callback_arg, "args": args, "pause_process": pause_process, "one_shot": one_shot}

    def _on_load(self) -> None:
        """Engine hook. Called when the timer is mounted to the active scene."""

    def _update(self, delta: float) -> None:
        """Counts down the timer duration. Triggers callback on expiration.

        Args:
            delta (float): Time since last frame in seconds.
        """
        self.time_left -= delta
        if self.time_left <= 0:
            self.callback(*self.args)
            if self.one_shot:
                self.do_kill = True
                return
            self.time_left += self.time

    def kill(self) -> None:
        """Kills the timer object and removes it from the scene graph."""
        Globals.scene.remove_object(self)


from ..engine.serializer import Serializer

Serializer.register_class(Timer)
