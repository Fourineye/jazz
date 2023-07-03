"""
    Contains different classes for controlling animations
"""

import pygame
from pygame import USEREVENT
from pygame.event import Event

from .scene import Scene
from .utils import clamp, map_range


class Tween:
    """Tween for animation"""

    def __init__(self, obj, prop, values, time, **kwargs):
        self.game_process = kwargs.get("game_process", True)
        self.pause_process = kwargs.get("pause_process", False)
        self.obj = obj
        self.prop = prop
        self.values = values
        self.last_val = len(self.values) - 1
        self.a_time = time
        self.time = 0
        self.loop = kwargs.get("loop", False)
        self.playing = kwargs.get("playing", False)
        self.end_event = Event(
            USEREVENT, {"source": "Tween", "flag": kwargs.get("flag", None)}
        )

    def process(self, delta: float):
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
        if len(self.values) > 2:
            a_time = self.a_time / self.last_val
            i = int(map_range(self.time, 0, self.a_time, 0, self.last_val))
            if i == self.last_val:
                value = self.values[-1]
            else:
                t_start, t_end = i * a_time, (i + 1) * a_time
                v_start, v_end = self.values[i], self.values[i + 1]
        else:
            t_start, t_end = 0, self.a_time
            v_start, v_end = self.values[0], self.values[1]
        value = map_range(self.time, t_start, t_end, v_start, v_end)
        setattr(self.obj, self.prop, value)

        if self.time >= self.a_time:
            self.time = 0
            pygame.event.post(self.end_event)
            if not self.loop:
                self.playing = False
        self.time += delta

    def play(self, from_beginning=True):
        """Starts the tween animation

        Args:
            from_beginning (bool, optional): An optional argument that
                determines if the tween starts over from the beginning.
                Defaults to True.
        """
        self.playing = True
        if from_beginning:
            self.time = 0

    def stop(self):
        """Stops the tween animation"""
        self.playing = False


class Animation:
    """Object to hold frame data for an animation"""

    def __init__(self, obj, frames, values, flag=None):
        self.obj = obj
        self.values = values
        self.frames = frames
        self.end_event = Event(
            USEREVENT, {"source": "Animation", "flag": flag, "obj": obj}
        )

    def play_frame(self, frame: int):
        """
        Set the object framedata for the given frame.

        Args:
            frame (int): The index of the framedata to set.
        """
        for param, framedata in self.values.items():
            data = framedata.get(frame)
            if data is not None:
                if param == "callback":
                    getattr(self.obj, data)()
                else:
                    setattr(self.obj, param, data)


class AnimationManager:
    """
    A component to hold multiple Animations and handle updating and
    playing them.
    """

    def __init__(self, animations=None, tweens=None, **kwargs):
        self.scene: Scene = None
        self.root: Application = None
        self.game_process = kwargs.get("game_process", True)
        self.pause_process = kwargs.get("pause_process", False)
        if animations is None:
            self.animations = {}
        else:
            self.animations = animations
        if tweens is None:
            self.tweens = {}
        else:
            self.tweens = tweens
        self.active_animation = None
        self.playing = False
        self.play_time = 0
        self.loop = False
        self.frame = 0

    def play_animation(self, animation: str, loop=False):
        """
        Starts an animation that has been previously loaded playing.

        Args:
            animation (str): Name of the Animation to play.
            loop (bool, optional): If the animation should loop when it finishes.
                Defaults to False.
        """
        new_animation = self.animations.get(animation)
        if new_animation is None:
            print("Animation does not exist")
            return
        if self.active_animation == new_animation and self.playing:
            self.loop = loop
        else:
            self.active_animation = new_animation
            self.playing = True
            self.play_time = 0
            self.loop = loop
            self.frame = 0

    def process(self, delta: float):
        """
        Called every frame, updates all animations and tweens that are children.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        for _name, tween in self.tweens.items():
            # print(_name)
            tween.process(delta)

        if self.playing:
            # print(self.frame)
            self.active_animation.play_frame(self.frame)
            self.frame += 1
            if self.frame >= self.active_animation.frames:
                self.frame = 0
                pygame.event.post(self.active_animation.end_event)
                if not self.loop:
                    self.playing = False

    def add_animation(self, name: str, animation: Animation):
        """
        Adds an Animation to the AnimationManager.

        Args:
            name (str): Name of the Animation being added.
            animation (Animation): Animation object to be added.
        """
        self.animations.update({name: animation})

    def add_tween(self, name: str, tween: Tween):
        """
        Adds a Tween to the AnimationManager

        Args:
            name (str): Name of the Tween being added.
            tween (Tween): Tween object to be added.
        """
        self.tweens.update({name: tween})


class Fade:
    """An object to create a screen fade effect"""

    def __init__(self, time, f_in=False, **kwargs):
        self.game_process = kwargs.get("game_process", True)
        self.pause_process = kwargs.get("pause_process", False)
        self.screen_layer = kwargs.get("screen_layer", True)
        self._z = 10
        self.display = pygame.display.get_surface()
        self.fade = self.display.copy()
        self.fade.fill("black")
        self.f_in = f_in
        if f_in:
            self.alpha = 255
        else:
            self.alpha = 0
        self.fade.set_alpha(self.alpha)
        self.rate = 255 / time
        self.timer = time
        self.active = True
        flag = kwargs.get("flag", None)
        self.end_event = Event(USEREVENT, {"source": "Fade", "flag": flag})

    def play(self, time, f_in=False):
        """
        Starts a fade animation

        Args:
            time (float): The amount of time in seconds the animation lasts.
            f_in (bool, optional): Determines if the animation fades in or out. Defaults to False.
        """
        self.f_in = f_in
        if f_in:
            self.alpha = 255
        else:
            self.alpha = 0
        self.fade.set_alpha(self.alpha)
        self.rate = 255 / time
        self.timer = time
        self.active = True

    def process(self, delta):
        """
        Called every frame, updates the animation if active.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        self.timer -= delta
        if self.f_in:
            self.alpha -= self.rate * delta
        else:
            self.alpha += self.rate * delta

        self.fade.set_alpha(clamp(self.alpha, 0, 255))
        if self.timer < 0 and self.active:
            pygame.event.post(self.end_event)
            self.active = False

    def draw(self, _display=None, _offset=None):
        """
        Draws the fade animation to the display.

        Args:
            _display (Surface, optional): For Engine compatibility. Defaults to None.
            _offset (Vector2, optional): For Engine compatibility. Defaults to None.
        """
        self.display.blit(self.fade, (0, 0))
