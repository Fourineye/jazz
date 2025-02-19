from base_test import Test

import jazz
from jazz import Globals


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
                text_size=24,
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
                text_size=24,
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
                text_size=24,
            )
        )
        self.add_object(
            jazz.Button(
                pos=(100, 280),
                size=(200, 50),
                anchor=(0, 0),
                callback=lambda: (
                    Globals.app.set_next_scene("Draw Test"),
                    self.stop(),
                ),
                label="Draw Test",
                text_size=24,
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
                text_size=24,
            )
        )
        self.bar = self.add_object(
            jazz.ProgressBar(
                10, 20, pos=(10, 10), anchor=(0, 0), size=(100, 20)
            )
        )

    def update(self, delta):
        self.bar.update_value(
            (self.bar.value + delta * 2) % self.bar.max_value
        )
