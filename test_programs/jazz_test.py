from test_animation import AnimationTest
from test_debug import DebugTest
from test_draw import DrawTest
from test_particles import ParticleTest
from test_render import RenderTest
from test_ui import UITest
from test_tweens import TweenTest

from jazz import Application

if __name__ == "__main__":
    app = Application(800, 800)
    scenes = [
        UITest,
        RenderTest,
        DebugTest,
        AnimationTest,
        DrawTest,
        ParticleTest,
        TweenTest,
    ]
    for scene in scenes:
        app.add_scene(scene)
    app.run()
