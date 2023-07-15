"""
    Contains different classes for controlling animations
"""

import pygame
from pygame import USEREVENT
from pygame.event import Event


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
