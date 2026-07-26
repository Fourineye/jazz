"""
Debug Showcase Scene loaded from JSON.
"""

import os
import sys

SHOWCASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SHOWCASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from jazz import Application, Scene

def load_debug_scene() -> Scene:
    json_path = os.path.join(os.path.dirname(__file__), "scenes", "debug_scene.json")
    scene = Scene.from_json(json_path)
    scene.toggle_debug()
    return scene

if __name__ == "__main__":
    app = Application(800, 800, "JSON Debug Showcase")
    scene = load_debug_scene()
    app.set_next_scene(scene)
    app.run()
