from test_animation import AnimationTest
from test_debug import DebugTest
from test_draw import DrawTest
from test_particles import ParticleTest
from test_render import RenderTest
from test_ui import UITest
from test_tweens import TweenTest

from jazz import Application, Globals, Label, Button, Vec2, Scene

SCENES = [
    UITest,
    RenderTest,
    DebugTest,
    AnimationTest,
    DrawTest,
    ParticleTest,
    TweenTest,
]


class Menu(Scene):
    name = "Menu"

    def on_load(self, _):
        def set_next(scene):
            def a():
                Globals.app.set_next_scene(scene)
                Globals.scene.stop()

            return a

        self.add_object(
            Label(text="Test Scenes", pos=(400, 100), anchor=(1, 0))
        )
        pos = Vec2(400, 150)
        for scene in Globals.app.get_scenes():
            if scene == self.name:
                continue
            self.add_object(
                Button(
                    pos=pos,
                    size=(200, 50),
                    anchor=(1, 0),
                    callback=set_next(scene),
                    label=scene,
                    text_size=18,
                )
            )
            pos += Vec2(0, 60)

    def on_unload(self) -> dict:
        return {"menu": self.name}


if __name__ == "__main__":
    app = Application(800, 800)
    app.add_scene(Menu)
    for scene in SCENES:
        app.add_scene(scene)
    app.run()
