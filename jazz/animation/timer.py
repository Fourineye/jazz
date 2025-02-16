from typing import Callable
import uuid

from ..global_dict import Globals


class Timer:
    def __init__(
        self,
        time_left: float,
        callback: Callable,
        args=tuple(),
        pause_process=False,
        one_shot=True,
    ):
        self.id = str(uuid.uuid1())
        self.time = time_left
        self.time_left = time_left
        self.callback = callback
        self.args = args
        self.game_process = True
        self.pause_process = pause_process
        self.one_shot = one_shot
        self.do_kill = False

    def _on_load(self): ...

    def _update(self, delta: float) -> None:
        self.time_left -= delta
        if self.time_left <= 0:
            self.callback(*self.args)
            if self.one_shot:
                self.do_kill = True
                return
            self.time_left += self.time

    def kill(self) -> None:
        Globals.scene.remove_object(self)
