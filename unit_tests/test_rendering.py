import unittest

from jazz import Label
from unit_tests.support import JazzTestCase


class TestRendering(JazzTestCase):
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

    def test_label_pos_and_draw_pos(self):
        lbl = Label(text="Hello World", pos=(100, 100))
        self.assertEqual(lbl.pos, (100, 100))
        self.assertEqual(lbl.draw_pos, lbl.pos + lbl._draw_offset)


if __name__ == "__main__":
    unittest.main()
