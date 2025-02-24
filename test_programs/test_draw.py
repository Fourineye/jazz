from base_test import Test

from jazz import Color, Draw, Globals, Rect, Vec2


class DrawTest(Test):
    name = "Draw Test"

    def __init__(self):
        super().__init__()
        self.test_lines = (
            Vec2(100, 700),
            Vec2(300, 500),
            Vec2(100, 500),
            Vec2(300, 700),
        )
        self.line_width = 1
        self.closed = False

    def on_load(self, data):
        Test.on_load(self, data)
        self.create_timer(0.1, self.iterate_width, ())
        self.create_timer(20, self.stop, ())

    def iterate_width(self):
        self.line_width += 0.2
        if self.line_width > 10:
            self.line_width = 1
            self.closed = not self.closed
        self.create_timer(0.1, self.iterate_width, ())

    def render(self):
        super().render()
        test_rect = Rect(
            500, 100, 100 + self.line_width * 10, 200 - self.line_width * 10
        )
        if self.closed:
            Draw.fill_circle(
                Vec2(600, 600), self.line_width * 10, Color("green")
            )
            Draw.fill_rect(test_rect, Color("red"))
        else:
            Draw.rect(test_rect, Color("red"), int(self.line_width))
            Draw.circle(
                Vec2(600, 600),
                self.line_width * 10,
                Color("green"),
                int(self.line_width),
            )
        Draw.lines(
            self.test_lines, Color("blue"), int(self.line_width), self.closed
        )
