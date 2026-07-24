import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pygame
from jazz import GameObject
from jazz.animation import Tween
from jazz.engine.resource_manager import ResourceManager
from jazz.global_dict import SETTINGS
from jazz.utils import load_ini, save_ini


class TestMinorImprovements(unittest.TestCase):
    def test_load_ini_with_open_file(self):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".ini") as tmp:
            tmp.write("[DISPLAY]\nwidth = 800\nheight = 600\n")
            tmp_path = tmp.name

        try:
            load_ini(tmp_path)
            self.assertEqual(str(SETTINGS["DISPLAY"]["width"]), "800")
            self.assertEqual(str(SETTINGS["DISPLAY"]["height"]), "600")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_add_surface_return_value(self):
        res = object.__new__(ResourceManager)
        res._surfaces = {}
        res._textures = {}
        pygame.init()
        surf = pygame.Surface((10, 10))
        returned_surf = res.add_surface(surf, "test_surf")
        self.assertIs(returned_surf, surf)
        self.assertIs(res.get_surface("test_surf"), surf)

    def test_tween_one_shot_lifecycle(self):
        class DummyObject(GameObject):
            def __init__(self):
                super().__init__()
                self.val = 0.0

        obj = DummyObject()

        # One shot tween (default)
        on_end_called = []
        t1 = Tween(obj, "val", 100, time=1.0, one_shot=True, on_end=lambda: on_end_called.append(True))
        t1.play()
        # Step 1: time advances from 0 to 1.0
        t1.update(1.0)
        # Step 2: time is now >= 1.0, completion triggers
        t1.update(0.0)

        self.assertFalse(t1.playing)
        self.assertTrue(t1.do_kill)
        self.assertTrue(on_end_called)
        self.assertEqual(obj.val, 100)

        # Non one-shot tween (one_shot=False)
        on_end_called_2 = []
        t2 = Tween(obj, "val", 200, time=1.0, one_shot=False, on_end=lambda: on_end_called_2.append(True))
        t2.play()
        t2.update(1.0)
        t2.update(0.0)

        self.assertFalse(t2.playing)
        self.assertFalse(t2.do_kill)
        self.assertTrue(on_end_called_2)
        self.assertEqual(obj.val, 200)


if __name__ == "__main__":
    unittest.main()
