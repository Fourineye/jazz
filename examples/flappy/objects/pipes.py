"""A pair of pipes: two static Bodies with a score gate Area in the gap between them."""

from jazz import COLLIDER_RECT, Area, Body, GameObject, Sprite

from config import LAYER_GATES, LAYER_NONE, LAYER_OBSTACLES, PIPE_GAP, PIXEL_SCALE, Z_PIPES, asset

PIPE_WIDTH = 26 * PIXEL_SCALE
PIPE_BODY_WIDTH = 24 * PIXEL_SCALE
PIPE_HEIGHT = 160 * PIXEL_SCALE


class PipePair(GameObject):
    """Top and bottom pipe with a scoring gate between them. Moving the pair moves every child."""

    def __init__(self, x: float, gap_center: float, **kwargs) -> None:
        """Initializes the PipePair.

        Args:
            x (float): Horizontal centre of the pipes.
            gap_center (float): Vertical centre of the gap.
        """
        kwargs.setdefault("z", Z_PIPES)
        super().__init__("PipePair", pos=(x, gap_center), **kwargs)
        offset = PIPE_GAP / 2 + PIPE_HEIGHT / 2
        self.top: Body = self.add_child(self._make_pipe(-offset, flip=True))
        self.bottom: Body = self.add_child(self._make_pipe(offset, flip=False))

        self.gate: Area = Area(
            name="Gate",
            layers=LAYER_GATES,
            collision_layers=LAYER_NONE,
            active=False,
            properties={"kind": "gate", "scored": False},
        )
        self.gate.add_collider(COLLIDER_RECT, w=6, h=PIPE_GAP)
        self.add_child(self.gate)

    @staticmethod
    def _make_pipe(y: float, flip: bool) -> Body:
        """Builds one static pipe Body with its collider and sprite.

        Args:
            y (float): Local vertical offset from the gap centre.
            flip (bool): Flips the sprite vertically for the top pipe.

        Returns:
            Body: The pipe body.
        """
        pipe = Body(
            name="Pipe",
            static=True,
            pos=(0, y),
            layers=LAYER_OBSTACLES,
            collision_layers=LAYER_NONE,
            properties={"kind": "pipe"},
        )
        pipe.add_collider(COLLIDER_RECT, w=PIPE_BODY_WIDTH, h=PIPE_HEIGHT)
        pipe.add_child(
            Sprite(
                texture=asset("pipe.png"),
                scale=(PIXEL_SCALE, PIXEL_SCALE),
                anchor=("center", "center"),
                flip_y=flip,
            )
        )
        return pipe
