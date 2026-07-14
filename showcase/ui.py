from numpy._core.defchararray import title
from base import Test

import jazz
from jazz import Globals, Vec2, Color


class UITest(Test):
    name = "UI Test"

    def __init__(self) -> None:
        """Initializes the UI Showcase test scene."""
        super().__init__()
        self.username_input = None
        self.email_input = None
        self.bar = None
        self.left_panel = None
        self.right_panel = None

    def on_load(self, data: dict) -> None:
        """Sets up the UI component panels and nested container structures.

        Args:
            data (dict): State dictionary passed from the menu.
        """
        Test.on_load(self, data)

        title_box = self.add_object(
            jazz.VBox(
                pos=(400,40), 
                anchor=(1,0), 
                bg_color=Color("maroon"), 
                border_color=Color("grey"),
                border_width=3,
                radius=5,
                padding=10,
                auto_size=True
            )
        )
        # Header Title
        title_box.add_child(
            jazz.Label(
                text="UI Components & Layouts Showcase",
                anchor=(1, 0),
                fontsize=32,
                text_color=Color("white"),
            )
        )

        # Subtitle / Footer Hint
        self.add_object(
            jazz.Label(
                text="Press [Space] to return to Menu",
                pos=(400, 720),
                anchor=(1, 0.5),
                fontsize=20,
                text_color=Color("gray"),
            )
        )

        # ----------------------------------------------------
        # LEFT PANEL: Interactive Settings Form Stack (VBox)
        # ----------------------------------------------------
        self.left_panel = self.add_object(
            jazz.VBox(
                pos=(45, 120),
                size=(340, 520),
                bg_color=(40, 40, 45),
                anchor=(0, 0),
                padding=20,
                spacing=25,
                align="center",
                radius=10,
                shadow_offset=(3, 5),
                shadow_blur=4,
                shadow_color=(0, 0, 0, 100)
            )
        )

        # Panel Header
        self.left_panel.add_child(
            jazz.Label(
                text="SETTINGS & FORM INPUTS",
                fontsize=20,
                text_color=Color("orange")
            )
        )

        # Username Field Row (HBox)
        user_row = jazz.HBox(spacing=10, align="center")
        user_row.add_child(
            jazz.Label(text="Username: ", fontsize=16, text_color=Color("white"))
        )
        self.username_input = user_row.add_child(
            jazz.TextBox(
                size=(160, 35),
                text="Alice",
                bg_color=(80, 80, 85),
                field_color=(30, 30, 35),
                text_color=(255, 255, 255),
                fontsize=16,
                radius=6,
                border_color=(120, 120, 130),
                border_width=1,
            )
        )
        self.left_panel.add_child(user_row)

        # Email Field Row (HBox)
        email_row = jazz.HBox(spacing=10, align="center")
        email_row.add_child(
            jazz.Label(text="Email:    ", fontsize=16, text_color=Color("white"))
        )
        self.email_input = email_row.add_child(
            jazz.TextBox(
                size=(160, 35),
                text="alice@example.com",
                bg_color=(80, 80, 85),
                field_color=(30, 30, 35),
                text_color=(255, 255, 255),
                fontsize=16,
                radius=6,
                border_color=(120, 120, 130),
                border_width=1,
            )
        )
        self.left_panel.add_child(email_row)

        # Progress / Health Bar Row (HBox)
        health_row = jazz.HBox(spacing=10, align="center")
        health_row.add_child(
            jazz.Label(text="Health:   ", fontsize=16, text_color=Color("white"))
        )
        self.bar = health_row.add_child(
            jazz.ProgressBar(
                0, 20, size=(160, 25), bg_color=(80, 80, 85), color=(100, 150, 250)
            )
        )
        self.left_panel.add_child(health_row)

        # Actions Button Row (HBox)
        actions_row = jazz.HBox(spacing=15, align="center")
        
        def on_clear() -> None:
            self.username_input.set_text("")
            self.email_input.set_text("")
            
        def on_submit() -> None:
            user = self.username_input._text.text_content
            email = self.email_input._text.text_content
            print(f"Submitted form: Username='{user}', Email='{email}'")

        actions_row.add_child(
            jazz.Button(
                size=(100, 40),
                label="Clear",
                callback=on_clear
            )
        )
        actions_row.add_child(
            jazz.Button(
                size=(100, 40),
                label="Submit",
                callback=on_submit
            )
        )
        self.left_panel.add_child(actions_row)

        # ----------------------------------------------------
        # RIGHT PANEL: Layout Engine Demonstration (VBox)
        # ----------------------------------------------------
        self.right_panel = self.add_object(
            jazz.VBox(
                pos=(415, 120),
                size=(340, 520),
                bg_color=(30, 45, 70),
                anchor=(0, 0),
                padding=20,
                spacing=20,
                align="center",
                radius=10,
                shadow_offset=(3, 5),
                shadow_blur=4,
                shadow_color=(0, 0, 0, 100)
            )
        )

        # Panel Header
        self.right_panel.add_child(
            jazz.Label(
                text="LAYOUT ENGINE ALIGNMENTS",
                fontsize=20,
                text_color=Color("cyan")
            )
        )

        # HBox Vertical Alignment Demo (Top, Middle, Bottom)
        self.right_panel.add_child(
            jazz.Label(text="HBox Cross-Alignment (Center):", fontsize=14, text_color=Color("gray"))
        )
        hbox_align = jazz.HBox(spacing=10, align="center")
        hbox_align.add_child(jazz.Button(size=(70, 25), label="Short"))
        hbox_align.add_child(jazz.Button(size=(70, 55), label="Tall"))
        hbox_align.add_child(jazz.Button(size=(70, 40), label="Mid"))
        self.right_panel.add_child(hbox_align)

        # Button Styles Demo
        self.right_panel.add_child(
            jazz.Label(text="Procedural Button Styles:", fontsize=14, text_color=Color("gray"))
        )
        
        styles_row = jazz.HBox(spacing=10, align="center")
        
        styles_row.add_child(
            jazz.Button(
                size=(70, 35),
                label="Flat",
                style="flat",
                unpressed_color=Color(120, 60, 180),
                pressed_color=Color(90, 45, 140),
                hover_color=Color(140, 70, 210)
            )
        )
        styles_row.add_child(
            jazz.Button(
                size=(70, 35),
                label="Grad",
                style="gradient",
                unpressed_color=Color(60, 150, 100),
                pressed_color=Color(40, 100, 70),
                hover_color=Color(80, 180, 120)
            )
        )
        styles_row.add_child(
            jazz.Button(
                size=(70, 35),
                label="Skeuo",
                style="skeuomorphic",
                unpressed_color=Color(180, 100, 60),
                pressed_color=Color(130, 70, 40),
                hover_color=Color(210, 120, 70)
            )
        )
        styles_row.add_child(
            jazz.Button(
                size=(70, 35),
                label="Glossy",
                style="glossy",
                unpressed_color=Color(180, 60, 100),
                pressed_color=Color(130, 40, 70),
                hover_color=Color(210, 80, 120)
            )
        )
        
        self.right_panel.add_child(styles_row)

        # VBox Horizontal Alignment Demo (Left, Center, Right)
        self.right_panel.add_child(
            jazz.Label(text="VBox Horizontal Alignments:", fontsize=14, text_color=Color("gray"))
        )
        
        align_row = jazz.HBox(spacing=15, align="center")
        
        v_left = jazz.VBox(align="left", spacing=4, padding=0)
        v_left.add_child(jazz.Label(text="Left 1", fontsize=12))
        v_left.add_child(jazz.Label(text="Left 2 (long)", fontsize=12))
        align_row.add_child(v_left)
        
        v_center = jazz.VBox(align="center", spacing=4, padding=0)
        v_center.add_child(jazz.Label(text="Center 1", fontsize=12))
        v_center.add_child(jazz.Label(text="Center 2 (long)", fontsize=12))
        align_row.add_child(v_center)
        
        v_right = jazz.VBox(align="right", spacing=4, padding=0)
        v_right.add_child(jazz.Label(text="Right 1", fontsize=12))
        v_right.add_child(jazz.Label(text="Right 2 (long)", fontsize=12))
        align_row.add_child(v_right)
        
        self.right_panel.add_child(align_row)

        # UIContainer Non-Rendering Stack Demo
        self.right_panel.add_child(
            jazz.Label(text="UIContainer (Logical Group):", fontsize=14, text_color=Color("gray"))
        )
        
        logical_container = jazz.UIContainer(layout_type="vertical", spacing=8, align="center")
        logical_container.add_child(
            jazz.Label(text="Nested Item A", fontsize=14, text_color=Color("yellow"))
        )
        logical_container.add_child(
            jazz.Label(text="Nested Item B", fontsize=14, text_color=Color("yellow"))
        )
        self.right_panel.add_child(logical_container)

    def update(self, delta: float) -> None:
        """Updates the animated health/progress bar value over time.

        Args:
            delta (float): The time delta in seconds since the last frame.
        """
        self.bar.update_value(
            (self.bar.value + delta * 2) % self.bar.max_value
        )

        if Globals.key.press("d"):
            self.toggle_debug()


if __name__ == "__main__":
    from jazz import Application
    app = Application(800, 800)
    app.add_scene(UITest)
    app.run()
