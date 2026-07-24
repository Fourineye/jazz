import unittest
import sys
import os

# Add parent directory to path to import jazz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jazz import GameObject, Vec2
from jazz.components import VBox, HBox, UIContainer
import jazz.global_dict

class MockResource:
    def get_texture(self, name):
        if isinstance(name, MockTexture):
            return name
        return MockTexture()
    def add_texture(self, texture, id, b):
        if isinstance(texture, MockTexture):
            return texture
        if hasattr(texture, "get_size"):
            return MockTexture(texture.get_size())
        return MockTexture()
    def get_color(self, color):
        return MockTexture()
    def get_font(self, size=24):
        return MockFontObject()
    def get_styled_texture(self, size, color, radius=0, shadow_offset=(0, 0), shadow_color=None, shadow_blur=0, style="flat", border_color=None, border_width=0):
        return MockTexture(size)

class MockFontObject:
    def render(self, *args, **kwargs):
        return MockTexture()
    def size(self, text):
        return (len(text) * 10, 20)
    def get_height(self):
        return 20

class MockTexture:
    def __init__(self, size=(32, 32)):
        self.width = size[0]
        self.height = size[1]
    def draw(self, *args):
        pass
    def get_rect(self):
        return MockRect(self.width, self.height)

class MockRect:
    def __init__(self, w, h):
        self.size = (w, h)

class MockInputHandler:
    def start_text_input(self):
        pass
    def stop_text_input(self):
        pass

class TestUIContainers(unittest.TestCase):
    def setUp(self):
        self.old_resource = jazz.global_dict.Globals.resource
        self.old_key = jazz.global_dict.Globals.key
        jazz.global_dict.Globals.resource = MockResource()
        jazz.global_dict.Globals.key = MockInputHandler()

    def tearDown(self):
        jazz.global_dict.Globals.resource = self.old_resource
        jazz.global_dict.Globals.key = self.old_key

    def test_vbox_vertical_stacking(self):
        # Create a vertical container with spacing 5, padding 10
        vbox = VBox(spacing=5, padding=10)
        
        # Add mock child sprites
        child1 = GameObject(name="child1")
        child1._size = Vec2(30, 20)
        child2 = GameObject(name="child2")
        child2._size = Vec2(40, 15)
        
        vbox.add_child(child1)
        vbox.add_child(child2)
        
        # Force a layout pass
        vbox.layout()
        
        # Sizes should influence positioning
        # Left padding: 10. Center alignment (default for VBox).
        # Max width of children: 40.
        # So vbox width: padding_left + max_child_width + padding_right = 10 + 40 + 10 = 60.
        # Child 1: width 30. (40 - 30) / 2 = 5 center offset. local_pos.x = left + offset = 10 + 5 = 15.
        # Child 2: width 40. (40 - 40) / 2 = 0 center offset. local_pos.x = left + offset = 10 + 0 = 10.
        self.assertAlmostEqual(child1.local_pos.x, 15, places=2)
        self.assertAlmostEqual(child2.local_pos.x, 10, places=2)
        
        # Vertical: starting from padding top (10)
        # Child 1 Y: 10
        # Child 2 Y: 10 (child1 Y) + 20 (child1 height) + 5 (spacing) = 35
        self.assertAlmostEqual(child1.local_pos.y, 10, places=2)
        self.assertAlmostEqual(child2.local_pos.y, 35, places=2)
        
        # VBox size should auto_size:
        # Width: 60
        # Height: top padding (10) + heights (20 + 15) + spacing (5) + bottom padding (10) = 60
        self.assertAlmostEqual(vbox._size.x, 60, places=2)
        self.assertAlmostEqual(vbox._size.y, 60, places=2)

    def test_vbox_alignments(self):
        # Test start/left alignment
        vbox_left = VBox(align="left", padding=5, spacing=0)
        child = GameObject()
        child._size = Vec2(20, 10)
        vbox_left.add_child(child)
        vbox_left.layout()
        self.assertAlmostEqual(child.local_pos.x, 5, places=2)

        # Test end/right alignment with explicit size
        vbox_right = VBox(align="right", padding=5, spacing=0, size=(100, 100))
        child2 = GameObject()
        child2._size = Vec2(20, 10)
        vbox_right.add_child(child2)
        vbox_right.layout()
        # right align: container_width - padding_right - child_width = 100 - 5 - 20 = 75
        self.assertAlmostEqual(child2.local_pos.x, 75, places=2)

    def test_hbox_horizontal_stacking(self):
        # Create a horizontal container with spacing 10, padding 5
        hbox = HBox(spacing=10, padding=5)
        
        child1 = GameObject(name="child1")
        child1._size = Vec2(30, 20)
        child2 = GameObject(name="child2")
        child2._size = Vec2(40, 15)
        
        hbox.add_child(child1)
        hbox.add_child(child2)
        hbox.layout()
        
        # Vertical alignment center (default): max height is 20
        # Child 1: height 20. local_pos.y = top_padding + (max_h - child_h)/2 = 5 + (20 - 20)/2 = 5
        # Child 2: height 15. local_pos.y = top_padding + (max_h - child_h)/2 = 5 + (20 - 15)/2 = 7.5
        self.assertAlmostEqual(child1.local_pos.y, 5, places=2)
        self.assertAlmostEqual(child2.local_pos.y, 7.5, places=2)
        
        # Horizontal stacking starting from left_padding (5)
        # Child 1 X: 5
        # Child 2 X: 5 (child1 X) + 30 (child1 width) + 10 (spacing) = 45
        self.assertAlmostEqual(child1.local_pos.x, 5, places=2)
        self.assertAlmostEqual(child2.local_pos.x, 45, places=2)
        
        # HBox auto_size size:
        # Width: left_padding (5) + child1_w (30) + spacing (10) + child2_w (40) + right_padding (5) = 90
        # Height: top_padding (5) + max_h (20) + bottom_padding (5) = 30
        self.assertAlmostEqual(hbox._size.x, 90, places=2)
        self.assertAlmostEqual(hbox._size.y, 30, places=2)

    def test_ui_container_layout_policies(self):
        # UIContainer - vertical layout policy
        container = UIContainer(layout_type="vertical", padding=10, spacing=2)
        child1 = GameObject()
        child1._size = Vec2(10, 10)
        child2 = GameObject()
        child2._size = Vec2(20, 20)
        
        container.add_child(child1)
        container.add_child(child2)
        container.layout()
        
        # Vertical flow:
        # Child 1 Y: 10
        # Child 2 Y: 10 + 10 + 2 = 22
        self.assertAlmostEqual(child1.local_pos.y, 10, places=2)
        self.assertAlmostEqual(child2.local_pos.y, 22, places=2)
        
        # Auto size:
        # Width: left (10) + max_w (20) + right (10) = 40
        # Height: top (10) + sum_h (10 + 20) + spacing (2) + bottom (10) = 52
        self.assertAlmostEqual(container.size.x, 40, places=2)
        self.assertAlmostEqual(container.size.y, 52, places=2)

    def test_visibility_filtering(self):
        vbox = VBox(spacing=5, padding=0)
        child1 = GameObject()
        child1._size = Vec2(10, 10)
        child2 = GameObject()
        child2._size = Vec2(10, 10)
        
        vbox.add_child(child1)
        vbox.add_child(child2)
        
        vbox.layout()
        self.assertAlmostEqual(child2.local_pos.y, 15, places=2)
        
        # Make child1 invisible
        child1.visible = False
        vbox.layout()
        
        # child1 should be skipped, so child2 sits at top padding (0)
        self.assertAlmostEqual(child2.local_pos.y, 0, places=2)
        self.assertAlmostEqual(vbox._size.y, 10, places=2)

    def test_child_scaling(self):
        vbox = VBox(spacing=10, padding=0)
        child1 = GameObject()
        child1._size = Vec2(10, 10)
        child1._scale = Vec2(2, 2)  # effectively 20x20
        
        child2 = GameObject()
        child2._size = Vec2(10, 10)
        
        vbox.add_child(child1)
        vbox.add_child(child2)
        vbox.layout()
        
        # Child 1: scaled height 20. Child 2 starts at: 20 + 10 = 30
        self.assertAlmostEqual(child2.local_pos.y, 30, places=2)

    def test_button_dynamic_hitbox(self):
        from jazz.components import Button
        vbox = VBox(spacing=5, padding=10, pos=(100, 100))
        button = Button(size=(50, 20))
        vbox.add_child(button)
        vbox.layout()
        
        # Button should sit at padding top (10) and padding left (10)
        # button.pos = vbox.pos + button.local_pos = (100, 100) + (35, 20) = (135, 120)
        # draw_offset is - (50/2, 20/2) = -(25, 10)
        # button.rect.topleft = (135, 120) - (25, 10) = (110, 110)
        self.assertAlmostEqual(button.rect.x, 110, places=2)
        self.assertAlmostEqual(button.rect.y, 110, places=2)
        
        # Now move the container to (200, 300)
        vbox.pos = Vec2(200, 300)
        vbox.layout()
        
        # The button's local_pos remains (35, 20)
        # button.pos = (200, 300) + (35, 20) = (235, 320)
        # button.rect.topleft = (235, 320) - (25, 10) = (210, 310)
        self.assertAlmostEqual(button.rect.x, 210, places=2)
        self.assertAlmostEqual(button.rect.y, 310, places=2)

    def test_textbox_scroll_bounds(self):
        from jazz.components import TextBox
        class MockFont:
            def size(self, text):
                return (len(text) * 10, 20)
            def get_height(self):
                return 20
            def render(self, text, antialias, color):
                return MockTexture()
        
        tb = TextBox(size=(100, 30), font=MockFont(), text="1234567890123")
        
        # Unfocused should show prefix: "12345678" (80px < 88px available)
        tb.active = False
        self.assertEqual(tb.text, "1234567890123")
        self.assertEqual(tb._text.text_content, "12345678")
        
        # Focused should show suffix: "67890123" (80px < 88px available)
        tb.active = True
        self.assertEqual(tb.text, "1234567890123")
        self.assertEqual(tb._text.text_content, "67890123")

if __name__ == "__main__":
    unittest.main()
