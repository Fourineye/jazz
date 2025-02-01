from random import randint

import jazz
from jazz import Globals, Vec2
from jazz.utils import random_color

SPRITES: int = 10000
MIN_SIZE: int = 50
MAX_SIZE: int = 200

class RenderTest(jazz.Scene):
    name = "Render Test"
    def __init__(self):
        super().__init__()
        self.sprite_count = SPRITES // 10
    
    def on_load(self, _):
        for _ in range(self.sprite_count):
            self.add_object(
                jazz.Sprite(
                    color=random_color(), pos=(randint(5, 795), randint(5, 795)), size = Vec2(randint(MIN_SIZE, MAX_SIZE), randint(MIN_SIZE, MAX_SIZE))
                )
            )
        self.set_timer(6, self.record_fps, ())
        

    def update(self, delta):
        Globals.app.set_caption(f"{Globals.app.get_fps():.1f} fps")

    def record_fps(self):
        print(f"{self.sprite_count} Sprites : {Globals.app.get_fps():.1f} fps")
        
        if self.sprite_count < SPRITES:
            self.set_timer(6, self.record_fps, ())
            self.sprite_count += SPRITES // 10
            for _ in range(SPRITES // 10):
                self.add_object(
                    jazz.Sprite(
                        color=random_color(), pos=(randint(5, 795), randint(5, 795)), size = Vec2(randint(MIN_SIZE, MAX_SIZE), randint(MIN_SIZE, MAX_SIZE))
                    )
                )
        else:
            self.stop()

if __name__ == "__main__":
    app = jazz.Application(800, 800)
    app.add_scene(RenderTest)
    app.run()
