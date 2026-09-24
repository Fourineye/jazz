"""
UI Showcase Scene loaded from JSON.
"""

import os
import sys

# Ensure project root is in sys.path when executed directly
EXAMPLES_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from jazz import Application, Scene

def load_ui_scene() -> Scene:
    json_path = os.path.join(os.path.dirname(__file__), "scenes", "ui_scene.json")
    return Scene.from_json(json_path)

if __name__ == "__main__":
    app = Application(800, 800, "JSON UI Showcase")
    scene = load_ui_scene()
    app.set_next_scene(scene)
    app.run()
