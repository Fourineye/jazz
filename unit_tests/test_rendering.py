import os
import sys
import unittest

# Set SDL to use dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Add parent directory to path to import jazz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
pygame.init()

from jazz import Application, Globals, Label, Scene


class TestRendering(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize jazz application
        cls.app = Application(800, 800)

        # Create and set dummy active scene
        class DummyScene(Scene):
            name = "Dummy"

            def on_load(self, _):
                pass

        cls.app.add_scene(DummyScene)
        cls.app._active_scene = DummyScene()
        Globals.scene = cls.app._active_scene

    def test_label_rendering_normal(self):
        lbl = Label(text="Hello")
        self.assertTrue(lbl._size.x > 0)
        self.assertEqual(lbl.text_content, "Hello")

    def test_label_rendering_empty_on_init(self):
        lbl = Label(text="")
        self.assertEqual(lbl._size.x, 0)
        self.assertEqual(lbl.text_content, "")

    def test_label_rendering_empty_on_set_text(self):
        lbl = Label(text="Hello")
        lbl.set_text("")
        self.assertEqual(lbl._size.x, 0)
        self.assertEqual(lbl.text_content, "")


if __name__ == "__main__":
    unittest.main()
