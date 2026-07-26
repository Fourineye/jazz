"""
Tweens Showcase Scene loaded from JSON.
"""

import os
import sys

SHOWCASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(SHOWCASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from jazz import Application, Scene

def load_tweens_scene() -> Scene:
    json_path = os.path.join(os.path.dirname(__file__), "scenes", "tweens_scene.json")
    return Scene.from_json(json_path)

if __name__ == "__main__":
    app = Application(800, 800, "JSON Tweens Showcase")
    scene = load_tweens_scene()
    app.set_next_scene(scene)
    app.run()
