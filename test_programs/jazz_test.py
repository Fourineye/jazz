from random import randint

import jazz
from jazz import Globals, Vec2, Draw
from jazz.utils import random_color, Color, Rect
from jazz.particles import ParticleEmitter

SPRITES: int = 50000
TIME: float = 1.5
MIN_SIZE: int = 5
MAX_SIZE: int = 20


class Test(jazz.Scene):
    def __init__(self):
        super().__init__()
        self._caption_timer = 0.5

    def on_load(self, _):
        self.update_title()

    def update_title(self):
        Globals.app.set_caption(f"{Globals.app.get_fps():2.2f} fps")
        self.set_timer(self._caption_timer, self.update_title, ())


class UITest(Test):
    name = "UI Test"

    def __init__(self):
        super().__init__()
        self.bar = None

    def on_load(self, data):
        Test.on_load(self, data)
        # self.camera.debug = True
        self.add_object(
            jazz.Label(text="Test Scenes", pos=(200, 50), anchor=(1, 0))
        )
        self.add_object(
            jazz.Button(
                pos=(100, 100),
                size=(200, 50),
                anchor=(0, 0),
                callback=lambda: (
                    Globals.app.set_next_scene("Animation Test"),
                    self.stop(),
                ),
                label="Animation",
                text_size=24
            )
        )
        self.add_object(
            jazz.Button(
                pos=(100, 160),
                size=(200, 50),
                anchor=(0, 0),
                callback=lambda: (
                    Globals.app.set_next_scene("Debug Test"),
                    self.stop(),
                ),
                label="Debug",
                text_size=24
            )
        )
        self.add_object(
            jazz.Button(
                pos=(100, 220),
                size=(200, 50),
                anchor=(0, 0),
                callback=lambda: (
                    Globals.app.set_next_scene("Render Test"),
                    self.stop(),
                ),
                label="Stress Test",
                text_size=24
            )
        )
        self.add_object(
            jazz.Button(
                pos=(100, 280),
                size=(200, 50),
                anchor=(0, 0),
                callback=lambda: (
                    Globals.app.set_next_scene("Primative Test"),
                    self.stop(),
                ),
                label="Draw Test",
                text_size=24
            )
        )
        self.add_object(
            jazz.Button(
                pos=(100, 340),
                size=(200, 50),
                anchor=(0, 0),
                callback=lambda: (
                    Globals.app.set_next_scene("Particle Test"),
                    self.stop(),
                ),
                label="Particle Test",
                text_size=24
            )
        )
        self.bar = jazz.ProgressBar(
            10, 20, pos=(10, 10), anchor=(0, 0), size=(100, 20)
        )
        self.add_object(self.bar)

    def update(self, delta):
        self.bar.update_value((self.bar.value + delta * 2) % self.bar.max_value)


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
        # Globals.app.set_caption(f"{Globals.app.get_fps():.1f} fps")
        if Globals.key.press("space"):
            self.stop()

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


class DebugTest(Test):
    name = "Debug Test"

    def __init__(self):
        super().__init__()
        self.square = None

    def on_load(self, data):
        Test.on_load(self, data)
        self.toggle_debug()
        self.square = jazz.Body(pos=(400, 400))
        self.square.add_collider("Rect", w=100, h=100)
        self.square.add_child(jazz.Sprite(scale=Vec2(10, 10)))

        body = jazz.Body(pos=(100, 100))
        body.add_collider("Circle", radius=50)
        self.add_object(body)
        self.add_object(self.square)
        Globals.app.set_next_scene("UI Test")
        self.set_timer(10, self.stop, ())

    def update(self, delta):
        self.square.rotate(36 * delta)


class AnimationTest(Test):
    name = "Animation Test"

    def on_load(self, data):
        Test.on_load(self, data)
        self.add_object(
            jazz.AnimatedSprite(
                spritesheet="./test_assets/IDLE.png",
                sprite_dim=(96, 96),
                pos=(400, 400),
                scale=Vec2(5, 5),
            ),
        )
        Globals.app.set_next_scene("UI Test")
        self.set_timer(5, self.stop, ())


class PrimativeTest(Test):
    name = "Primative Test"

    def __init__(self):
        super().__init__()
        self.test_lines = (
            Vec2(100, 700),
            Vec2(300, 500),
            Vec2(100, 500),
            Vec2(300, 700),
        )
        self.line_width = 1
        self.closed = False

    def on_load(self, data):
        Test.on_load(self, data)
        self.set_timer(0.1, self.iterate_width, ())
        Globals.app.set_next_scene("UI Test")
        self.set_timer(20, self.stop, ())

    def iterate_width(self):
        self.line_width += 0.2
        if self.line_width > 10:
            self.line_width = 1
            self.closed = not self.closed
        self.set_timer(0.1, self.iterate_width, ())

    def render(self):
        super().render()
        test_rect = Rect(
            500, 100, 100 + self.line_width * 10, 200 - self.line_width * 10
        )
        if self.closed:
            Draw.fill_circle(
                Vec2(600, 600), self.line_width * 10, Color("green")
            )
            Draw.fill_rect(test_rect, Color("red"))
        else:
            Draw.rect(test_rect, Color("red"), int(self.line_width))
            Draw.circle(
                Vec2(600, 600),
                self.line_width * 10,
                Color("green"),
                int(self.line_width),
            )
        Draw.lines(
            self.test_lines, Color("blue"), int(self.line_width), self.closed
        )


class ParticleTest(Test):
    name = "Particle Test"

    def on_load(self, _):
        super().on_load(_)
        Globals.app.set_next_scene("UI Test")
        self.add_object(ParticleEmitter(True, rate=50, pos=(400, 400), particle_spawn=50, emission_angles=[(-45, 45)]))
        self.set_timer(15, self.stop, ())

if __name__ == "__main__":
    app = jazz.Application(800, 800, experimental=True)
    scenes = [UITest, RenderTest, DebugTest, AnimationTest, PrimativeTest, ParticleTest]
    for scene in scenes:
        app.add_scene(scene)
    app.run()
