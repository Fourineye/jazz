from base import Test

import jazz
from jazz import Globals, Vec2


class UITest(Test):
    name = "UI Test"

    def __init__(self):
        super().__init__()
        self.bar = None
        self.text_box = None
        self.btn = None
        self.lbl = None
        self.vbox = None
        self.hbox = None
        self.ui_container = None

    def on_load(self, data):
        Test.on_load(self, data)

        self.lbl = self.add_object(
            jazz.Label(
                text="UI Components Showcase",
                pos=(400, 50),
                anchor=(1, 0),
                fontsize=32,
            )
        )

        self.text_box = self.add_object(
            jazz.TextBox(
                pos=(400, 150),
                anchor=(1, 0),
                size=(300, 40),
                text="Type here...",
                bg_color=(45, 45, 45),
                text_color=(255, 255, 255),
                on_change=lambda t: print(f"Text changed: {t}"),
                on_submit=lambda t: print(f"Submitted text: {t}"),
            )
        )

        self.bar = self.add_object(
            jazz.ProgressBar(
                0, 20, pos=(400, 250), anchor=(1, 0), size=(200, 25)
            )
        )

        self.btn = self.add_object(
            jazz.Button(
                pos=(400, 350),
                size=(200, 50),
                anchor=(1, 0),
                label="Click Me",
                callback=lambda: print("Button Clicked!"),
            )
        )

        # Visualize container stubs with colored backgrounds
        vbox_surf = jazz.Surface((100, 50))
        vbox_surf.fill((60, 60, 120))
        self.vbox = self.add_object(
            jazz.VBox(pos=(200, 500), anchor=(1, 0), texture=vbox_surf)
        )
        self.vbox.add_child(
            jazz.Label(
                text="VBox Stub",
                pos=(0, 0),
                anchor=(1, 1),
                fontsize=16,
            )
        )

        hbox_surf = jazz.Surface((100, 50))
        hbox_surf.fill((120, 60, 60))
        self.hbox = self.add_object(
            jazz.HBox(pos=(400, 500), anchor=(1, 0), texture=hbox_surf)
        )
        self.hbox.add_child(
            jazz.Label(
                text="HBox Stub",
                pos=(0, 0),
                anchor=(1, 1),
                fontsize=16,
            )
        )

        # UIContainer is a non-rendering GameObject, add label to make it visible
        self.ui_container = self.add_object(
            jazz.UIContainer(pos=(600, 500))
        )
        self.ui_container.add_child(
            jazz.Label(
                text="UIContainer Stub",
                pos=(0, 0),
                anchor=(1, 1),
                fontsize=16,
            )
        )

    def update(self, delta):
        self.bar.update_value(
            (self.bar.value + delta * 2) % self.bar.max_value
        )
