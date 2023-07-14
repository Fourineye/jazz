"""
    Contains different classes for controlling animations
"""

import pygame
from pygame import USEREVENT
from pygame.event import Event

from .baseObject import GameObject
from .scene import Scene
from .utils import clamp, map_range


def LINEAR(t):
    return t

def EASE_IN_QUADRATIC(t):
    return t ** 2

def EASE_OUT_QUADRATIC(t):
    return 1 - (1 - t) ** 2

def EASE_IN_OUT_QUADRATIC(t):
    return 2 * t ** 2 if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2

def EASE_IN_CUBIC(t):
    return t ** 3

def EASE_OUT_CUBIC(t):
    return 1 - (1 - t) ** 2

def EASE_IN_OUT_CUBIC(t):
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2

def EASE_IN_QUARTIC(t):
    return t ** 4

def EASE_OUT_QUARTIC(t):
    return 1 - (1 - t) ** 4

def EASE_IN_OUT_QUARTIC(t):
    return 8 * t ** 4 if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2

def EASE_IN_QUINTIC(t):
    return t ** 5

def EASE_OUT_QUINTIC(t):
    return 1 - (1 - t) ** 5

def EASE_IN_OUT_QUINTIC(t):
    return 16 * t ** 5 if t < 0.5 else 1 - (-2 * t + 2) ** 5 / 2

def EASE_IN_EXPO(t):
    return 0 if t == 0 else 2 ** (10 * t - 10)

def EASE_OUT_EXPO(t):
    return 1 if t == 1 else 1 - 2 ** (-10 * t)

def EASE_IN_OUT_EXPO(t):
    return 0 if t == 0 else 1 if t == 1 else 2 ** (20 * t - 10) / 2 if t < 0.5 else (2 - 2 ** (-20 * t + 10)) / 2

def EASE_IN_BACK(t):
    c1 = 1.70158
    c3 = c1 + 1
    return c3 * t ** 3 - c1 * t ** 2

def EASE_OUT_BACK(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def EASE_IN_OUT_BACK(t):
    c1 = 1.70158
    c2 = c1 * 1.525
    in_ = ((2 * t) ** 2 * ((c2 + 1) * 2 * t - c2)) / 2
    out_ = ((2 * t - 2) ** 2 * ((c2 + 1) * (t * 2 - 2) + c2) + 2) / 2
    return in_ if t < 0.5 else out_ #(Math.pow(2 * x - 2, 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2

EASINGS = [
    LINEAR,
    EASE_IN_QUADRATIC,
    EASE_OUT_QUADRATIC,
    EASE_IN_OUT_QUADRATIC,
    EASE_IN_CUBIC,
    EASE_OUT_CUBIC,
    EASE_IN_OUT_CUBIC,
    EASE_IN_QUARTIC,
    EASE_OUT_QUARTIC,
    EASE_IN_OUT_QUARTIC,
    EASE_IN_QUINTIC,
    EASE_OUT_QUINTIC,
    EASE_IN_OUT_QUINTIC,
    EASE_IN_EXPO,
    EASE_OUT_EXPO,
    EASE_IN_OUT_EXPO,
    EASE_IN_BACK,
    EASE_OUT_BACK,
    EASE_IN_OUT_BACK
]

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

        setattr(self.target_object, self.target_property, self._initial_value + self._delta_value * delta_factor)

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
