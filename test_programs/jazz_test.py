from random import randint

import jazz
from jazz import Globals, Vec2
from jazz.utils import random_color

SPRITES: int = 10000
MIN_SIZE: int = 5
MAX_SIZE: int = 20


class RenderTest(jazz.Scene):
    name = "Render Test"

    def __init__(self):
        super().__init__()
        self.sprite_count = SPRITES // 10

    def on_load(self, _):
        for _ in range(self.sprite_count):
            self.add_object(
                jazz.Sprite(
                    color=random_color(),
                    pos=(randint(5, 795), randint(5, 795)),
                    scale=Vec2(
                        randint(MIN_SIZE, MAX_SIZE), randint(MIN_SIZE, MAX_SIZE)
                    ),
                    rotation=randint(0, 90),
                )
            )
        self.set_timer(3, self.record_fps, ())
        Globals.app.set_next_scene("Rotation Test")

    def update(self, delta):
        Globals.app.set_caption(f"{Globals.app.get_fps():.1f} fps")

    def record_fps(self):
        print(f"{self.sprite_count} Sprites : {Globals.app.get_fps():.1f} fps")

        if self.sprite_count < SPRITES:
            self.set_timer(3, self.record_fps, ())
            self.sprite_count += SPRITES // 10
            for _ in range(SPRITES // 10):
                self.add_object(
                    jazz.Sprite(
                        color=random_color(),
                        pos=(randint(5, 795), randint(5, 795)),
                        scale=Vec2(
                            randint(MIN_SIZE, MAX_SIZE), randint(MIN_SIZE, MAX_SIZE)
                        ),
                        rotation=randint(0, 90),
                    )
                )
        else:
            self.stop()


class RotationTest(jazz.Scene):
    name = "Rotation Test"

    def __init__(self):
        super().__init__()
        self.square = None

    def on_load(self, _):
        self.camera.debug = True
        self.square = jazz.Sprite(scale=Vec2(10, 10), pos=(400, 400))
        self.add_object(self.square)
        Globals.app.set_next_scene("Animation Test")
        self.set_timer(10, Globals.app.stop, ())

    def update(self, delta):
        self.square.rotate(36 * delta)


class AnimationTest(jazz.Scene):
    name = "Animation Test"

    def on_load(self, data):
        self.add_object(
            jazz.AnimatedSprite(
                spritesheet="test_programs/Tiny Swords (Update 010)/Factions/Knights/Troops/Archer/Archer + Bow/Archer_Blue_(NoArms).png",
                sprite_dim=(192, 192),
                pos=(400, 400),
            ),
        )


if __name__ == "__main__":
    app = jazz.Application(800, 800, experimental=True)
    app.add_scene(AnimationTest)
    app.add_scene(RotationTest)
    app.add_scene(RenderTest)
    app.run()
