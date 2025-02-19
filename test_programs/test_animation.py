from base_test import Test

from jazz import AnimatedSprite, Globals, Vec2


class AnimationTest(Test):
    name = "Animation Test"

    def on_load(self, data):
        Test.on_load(self, data)
        self.add_object(
            AnimatedSprite(
                spritesheet="./test_assets/IDLE.png",
                sprite_dim=(96, 96),
                pos=(400, 400),
                scale=Vec2(5, 5),
            ),
        )
        Globals.app.set_next_scene("UI Test")
        self.create_timer(5, self.stop, ())
