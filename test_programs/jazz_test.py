from test_animation import AnimationTest
from test_debug import DebugTest
from test_draw import DrawTest
from test_particles import ParticleTest
from test_render import RenderTest
from test_ui import UITest

from jazz import Application

if __name__ == "__main__":
    app = Application(800, 800, experimental=True)
    scenes = [
        UITest,
        RenderTest,
        DebugTest,
        AnimationTest,
        DrawTest,
        ParticleTest,
    ]
    for scene in scenes:
        app.add_scene(scene)
    app.run()
