import jazz
from jazz import Globals, EASINGS, Tween, Sprite, Surface, Draw, Vec2, Color


def ball_sprite():
    ball = Surface((16, 16))
    ball.fill((255, 0, 255))
    ball.set_colorkey((255, 0, 255))
    with Draw.canvas(ball):
        Draw.circle(Vec2(8, 8), 8, Color(0, 0, 128))
    return ball


def background_sprite():
    bg = pygame.Surface((640, 480))
    bg.fill((64, 64, 64))
    for i in range(19):
        pygame.draw.line(
            bg, (128, 128, 200), (80, 50 + 20 * i), (320, 50 + 20 * i), 3
        )
    pygame.draw.line(bg, (128, 128, 128), (100, 50), (100, 410), 3)
    pygame.draw.line(bg, (128, 128, 128), (300, 50), (300, 410), 3)
    return bg


class Main(jazz.Scene):
    def __init__(self):
        super().__init__()
        self.bg = None

    def on_load(self, data):
        self.tweens = []
        self.points = []
        self.pause_timer = 2
        background = background_sprite()
        self.bg = self.add_object(jazz.Sprite(z=-1))
        self.bg.texture = background
        self.bg.set_anchor(0, 0)

        self.add_object(
            jazz.Label(text="0.0", pos=(100, 35), scale=(0.75, 0.75))
        )
        self.add_object(
            jazz.Label(text="1.0", pos=(300, 35), scale=(0.75, 0.75))
        )

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
                jazz.Vec2(300, 50 + 20 * i),
                2,
                easing=EASINGS[i],
                loop=False,
            )
            self.add_object(tween)
            self.tweens.append(tween)
            label = jazz.Label(
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
