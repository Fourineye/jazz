from random import randint

import jazz
from jazz import Globals, Vec2, Primatives
from jazz.utils import random_color, Color, Rect

SPRITES: int = 50000
TIME: float = 1.5
MIN_SIZE: int = 5
MAX_SIZE: int = 20


class RenderTest(jazz.Scene):
    name = "Render Test"

    def __init__(self):
        super().__init__()
        self.sprite_count = 1000

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
        self.set_timer(TIME, self.record_fps, ())
        Globals.app.set_next_scene("UI Test")

    def update(self, delta):
        Globals.app.set_caption(f"{Globals.app.get_fps():.1f} fps")

    def record_fps(self):
        print(f"{self.sprite_count} Sprites : {Globals.app.get_fps():.1f} fps")

        if Globals.app.get_fps() > 30 and self.sprite_count < SPRITES:
            self.set_timer(TIME, self.record_fps, ())
            self.sprite_count += 1000
            for _ in range(1000):
                self.add_object(
                    jazz.Sprite(
                        color=random_color(),
                        pos=(randint(5, 795), randint(5, 795)),
                        scale=Vec2(
                            randint(MIN_SIZE, MAX_SIZE),
                            randint(MIN_SIZE, MAX_SIZE),
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
        self.toggle_debug()
        self.square = jazz.Sprite(scale=Vec2(10, 10), pos=(400, 400))
        self.add_object(self.square)
        Globals.app.set_next_scene("UI Test")
        self.set_timer(10, self.stop, ())

    def update(self, delta):
        self.square.rotate(36 * delta)


class AnimationTest(jazz.Scene):
    name = "Animation Test"

    def on_load(self, data):
        self.add_object(
            jazz.AnimatedSprite(
                spritesheet="test_programs/test_assets/IDLE.png",
                sprite_dim=(96, 96),
                pos=(400, 400),
                scale=Vec2(5, 5)
            ),
        )
        Globals.app.set_next_scene("UI Test")
        self.set_timer(5, self.stop, ())

class UITest(jazz.Scene):
    name = "UI Test"

    def __init__(self):
        super().__init__()
        self.test_lines = (Vec2(100, 700), Vec2(300, 500), Vec2(100, 500), Vec2(300, 700))
        self.line_width = 1
        self.closed = False

    def on_load(self, _):
        # self.camera.debug = True
        self.add_object(
            jazz.Label(text="Test Scenes", pos=(200, 50), anchor=(1,0))
        )
        self.add_object(
            jazz.Button(pos=(100, 100), size=(200, 50), anchor=(0,0), callback=lambda:(Globals.app.set_next_scene("Animation Test"), self.stop()), label="Animation")
        )
        self.add_object(
            jazz.Button(pos=(100, 160), size=(200, 50), anchor=(0,0), callback=lambda:(Globals.app.set_next_scene("Rotation Test"), self.stop()), label="Rotation")
        )
        self.add_object(
            jazz.Button(pos=(100, 220), size=(200, 50), anchor=(0,0), callback=lambda:(Globals.app.set_next_scene("Render Test"), self.stop()), label="Stress Test")
        )
        self.set_timer(.1, self.iterate_width, ())
        self.update_title()
    
    def iterate_width(self):
        self.line_width += .2
        if self.line_width > 10:
            self.line_width = 1
            self.closed = not self.closed
        self.set_timer(.1, self.iterate_width, ())

    def update_title(self):
        Globals.app.set_caption(f"{Globals.app.get_fps():2.2f} fps")
        self.set_timer(0.5, self.update_title, ())

    def render(self):
        super().render()
        test_rect = Rect(500, 100, 100 + self.line_width * 10, 200 - self.line_width * 10)
        if self.closed:
            Primatives.fill_circle(Vec2(600, 600), self.line_width * 10, Color("green"))
            Primatives.fill_rect(test_rect, Color("red"))
        else:
            Primatives.rect(test_rect, Color("red"), int(self.line_width))
            Primatives.circle(Vec2(600, 600), self.line_width * 10, Color("green"), int(self.line_width))
        Primatives.lines(self.test_lines, Color("blue"), int(self.line_width), self.closed)

if __name__ == "__main__":
    app = jazz.Application(800, 800, experimental=True)
    scenes = [UITest, RenderTest, RotationTest, AnimationTest]
    for scene in scenes:
        app.add_scene(scene)
    app.run()
