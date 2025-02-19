from base_test import Test

from jazz import (
    EASINGS,
    Color,
    Draw,
    Label,
    Sprite,
    Surface,
    Tween,
    Vec2,
    Globals,
)


def ball_sprite():
    ball = Surface((16, 16))
    ball.fill((255, 0, 255))
    ball.set_colorkey((255, 0, 255))
    with Draw.canvas(ball):
        Draw.fill_circle(Vec2(8, 8), 8, Color(0, 0, 128))
    return ball


def background_sprite():
    bg = Surface((800, 800))
    bg.fill((64, 64, 64))
    with Draw.canvas(bg):
        for i in range(19):
            Draw.line(
                Vec2(80, 50 + 20 * i),
                Vec2(320, 50 + 20 * i),
                Color(128, 128, 200),
                3,
            )
        Draw.line(Vec2(100, 50), Vec2(100, 410), Color(128, 128, 128), 3)
        Draw.line(Vec2(300, 50), Vec2(300, 410), Color(128, 128, 128), 3)
    return bg


class TweenTest(Test):
    name = "Tweens"

    def __init__(self):
        super().__init__()
        self.bg = None

    def on_load(self, data):
        Test.on_load(self, data)
        Globals.app.set_next_scene("UI Test")
        self.tweens = []
        self.points = []
        self.pause_timer = 2
        background = background_sprite()
        self.bg = self.add_object(Sprite(z=-1))
        self.bg.texture = background
        self.bg.set_anchor(0, 0)

        self.add_object(Label(text="0.0", pos=(100, 35), scale=(0.75, 0.75)))
        self.add_object(Label(text="1.0", pos=(300, 35), scale=(0.75, 0.75)))

        # build ball sprite
        ball = ball_sprite()

        # Add tween displays
        for i in range(19):
            disp = Sprite(pos=(100, 50 + 20 * i))
            disp.texture = ball
            self.add_object(disp)
            self.points.append(disp)
            tween = Tween(
                disp,
                "pos",
                Vec2(300, 50 + 20 * i),
                2,
                easing=EASINGS[i],
                loop=False,
            )
            self.add_object(tween)
            self.tweens.append(tween)
            label = Label(
                text=EASINGS[i].__name__,
                pos=(350, 50 + 20 * i),
                scale=(0.75, 0.75),
            )
            label.set_anchor(horizontal="left")
            self.add_object(label)

    def update(self, delta):
        if self.pause_timer > 0 and not self.tweens[0].playing:
            self.pause_timer = max(self.pause_timer - delta, 0)
        elif self.pause_timer == 0:
            for point in self.points:
                point.pos = (100, point.y)
            [tween.play() for tween in self.tweens]
            self.pause_timer = 2
