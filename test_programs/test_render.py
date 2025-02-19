from random import randint

from base_test import Test

from jazz import Globals, Sprite, Vec2
from jazz.utils import random_color

SPRITES: int = 50000
TIME: float = 1.5
MIN_SIZE: int = 5
MAX_SIZE: int = 20


class TestSprite(Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rotation_direction = randint(-1, 1)
        self.rotation_speed = randint(15, 90)

    def update(self, delta):
        self.rotate(delta * self.rotation_direction * self.rotation_speed)


class RenderTest(Test):
    name = "Render Test"

    def __init__(self):
        super().__init__()
        self.sprite_count = 1000
        self._caption_timer = 0.1

    def on_load(self, data):
        Test.on_load(self, data)
        for _ in range(self.sprite_count):
            self.add_object(
                TestSprite(
                    color=random_color(),
                    pos=(randint(5, 795), randint(5, 795)),
                    scale=Vec2(
                        randint(MIN_SIZE, MAX_SIZE),
                        randint(MIN_SIZE, MAX_SIZE),
                    ),
                    rotation=randint(0, 90),
                )
            )
        self.create_timer(TIME, self.record_fps, ())
        Globals.app.set_next_scene("UI Test")

    def update(self, delta):
        # Globals.app.set_caption(f"{Globals.app.get_fps():.1f} fps")
        self.sprite_count += 5
        for _ in range(5):
            self.add_object(
                TestSprite(
                    color=random_color(),
                    pos=(randint(5, 795), randint(5, 795)),
                    scale=Vec2(
                        randint(MIN_SIZE, MAX_SIZE),
                        randint(MIN_SIZE, MAX_SIZE),
                    ),
                    rotation=randint(0, 90),
                )
            )

    def record_fps(self):
        print(f"{self.sprite_count} Sprites : {Globals.app.get_fps():.1f} fps")

        if Globals.app.get_fps() > 30 and self.sprite_count < SPRITES:
            self.create_timer(TIME, self.record_fps, ())
        else:
            self.stop()
