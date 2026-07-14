import os
from base import Test

from jazz import AnimatedSprite, Globals, Vec2


class AnimationTest(Test):
    name = "Animation Test"

    def on_load(self, data):
        Test.on_load(self, data)
        self.add_object(
            AnimatedSprite(
                spritesheet=os.path.join(os.path.dirname(__file__), "assets", "IDLE.png"),
                sprite_dim=(96, 96),
                pos=(400, 400),
                scale=Vec2(5, 5),
            ),
        )
        self.create_timer(5, self.stop, ())


if __name__ == "__main__":
    from jazz import Application
    app = Application(800, 800)
    app.add_scene(AnimationTest)
    app.run()
