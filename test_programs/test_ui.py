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

        self.bar = self.add_object(
            jazz.ProgressBar(
                0, 20, pos=(400, 400), anchor=(1, 0), size=(200, 25)
            )
        )

    def update(self, delta):
        self.bar.update_value(
            (self.bar.value + delta * 2) % self.bar.max_value
        )
