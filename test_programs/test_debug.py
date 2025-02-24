from base_test import Test

from jazz import Body, Globals, Sprite, Vec2, COLLIDER_RECT, COLLIDER_CIRCLE


class DebugTest(Test):
    name = "Debug Test"

    def __init__(self):
        super().__init__()
        self.square = None

    def on_load(self, data):
        Test.on_load(self, data)
        self.toggle_debug()
        self.square = Body(pos=(400, 400))
        self.square.add_collider(COLLIDER_RECT, w=100, h=100)
        self.square.add_child(Sprite(scale=Vec2(10, 10)))

        body = Body(pos=(100, 100))
        body.add_collider(COLLIDER_CIRCLE, radius=50)
        self.add_object(body)
        self.add_object(self.square)
        self.create_timer(10, self.stop, ())

    def update(self, delta):
        self.square.rotate(36 * delta)
