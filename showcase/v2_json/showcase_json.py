"""
Showcase Menu Runner loading all JSON-serialized showcase scenes via Scene.from_json().
"""

import os
import sys

SHOWCASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SHOWCASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from jazz import Application, Button, Globals, Label, Scene, Vec2


class MenuV2(Scene):
    """Menu Scene for navigating between JSON-serialized showcase scenes."""

    name = "MenuV2"

    def on_load(self, _=None) -> None:
        def make_scene_loader(scene_filename: str):
            def loader():
                json_path = os.path.join(os.path.dirname(__file__), "scenes", scene_filename)
                new_scene = Scene.from_json(json_path)
                Globals.app.set_next_scene(new_scene)
                Globals.scene.stop()

            return loader

        self.add_object(
            Label(
                text="JSON Showcase Menu (Deserialized Scenes)",
                pos=(400, 50),
                anchor=("center", "top"),
                fontsize=24,
            )
        )

        scenes = [
            ("UI Scene (JSON)", "ui_scene.json"),
            ("Animation Scene (JSON)", "animation_scene.json"),
            ("Physics Scene (JSON)", "physics_scene.json"),
            ("Tweens Scene (JSON)", "tweens_scene.json"),
            ("Render Scene (JSON)", "render_scene.json"),
            ("Debug Scene (JSON)", "debug_scene.json"),
            ("Draw Scene (JSON)", "draw_scene.json"),
            ("Particles Scene (JSON)", "particles_scene.json"),
        ]

        pos = Vec2(400, 120)
        for label_text, filename in scenes:
            self.add_object(
                Button(
                    pos=pos,
                    size=(320, 45),
                    anchor=("center", "top"),
                    callback=make_scene_loader(filename),
                    label=label_text,
                    text_size=16,
                )
            )
            pos += Vec2(0, 55)


if __name__ == "__main__":
    app = Application(800, 800, "JSON Showcase Menu")
    app.add_scene(MenuV2)
    app.set_next_scene("MenuV2")
    app.run()
