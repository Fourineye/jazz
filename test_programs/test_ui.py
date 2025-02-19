from base_test import Test

import jazz
from jazz import Globals, Vec2


class UITest(Test):
    name = "UI Test"

    def __init__(self):
        super().__init__()
        self.bar = None

    def on_load(self, data):
        Test.on_load(self, data)
        # self.toggle_debug()

        def set_next(scene):
            def a():
                Globals.app.set_next_scene(scene)
                Globals.scene.stop()

            return a

        self.add_object(
            jazz.Label(text="Test Scenes", pos=(400, 100), anchor=(1, 0))
        )
        pos = Vec2(400, 150)
        for scene in Globals.app.get_scenes():
            if scene == self.name:
                continue
            self.add_object(
                jazz.Button(
                    pos=pos,
                    size=(200, 50),
                    anchor=(1, 0),
                    callback=set_next(scene),
                    label=scene,
                    text_size=18,
                )
            )
            pos += Vec2(0, 60)

        self.bar = self.add_object(
            jazz.ProgressBar(0, 20, pos=pos, anchor=(1, 0), size=(200, 25))
        )

    def update(self, delta):
        self.bar.update_value(
            (self.bar.value + delta * 2) % self.bar.max_value
        )
