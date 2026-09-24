"""Scrolling ground strip, optionally solid so the bird can crash into it."""

from jazz import COLLIDER_RECT, Body, GameObject, Sprite, Vec2

from config import GROUND_Y, HEIGHT, LAYER_NONE, LAYER_OBSTACLES, PIXEL_SCALE, WIDTH, Z_GROUND, asset

# The ground texture's stripe pattern repeats every 12 art pixels
TILE_PERIOD = 12 * PIXEL_SCALE


class Ground(GameObject):
    """Ground strip along the bottom of the screen that scrolls by wrapping its texture."""

    def __init__(self, solid: bool = False, **kwargs) -> None:
        """Initializes the Ground.

        Args:
            solid (bool, optional): Adds a static Body on the obstacle layer. Defaults to False.
        """
        kwargs.setdefault("z", Z_GROUND)
        super().__init__("Ground", pos=(0, GROUND_Y), **kwargs)
        self.offset: float = 0.0
        self.strip: Sprite = self.add_child(
            Sprite(
                texture=asset("ground.png"),
                scale=(PIXEL_SCALE, PIXEL_SCALE),
                anchor=("left", "top"),
            )
        )
        if solid:
            depth = HEIGHT - GROUND_Y
            body = Body(
                name="GroundBody",
                static=True,
                pos=(WIDTH / 2, depth / 2),
                layers=LAYER_OBSTACLES,
                collision_layers=LAYER_NONE,
                properties={"kind": "ground"},
            )
            body.add_collider(COLLIDER_RECT, w=WIDTH * 2, h=depth)
            self.add_child(body)

    def scroll(self, distance: float) -> None:
        """Scrolls the ground texture left.

        Args:
            distance (float): Distance in pixels to scroll.
        """
        self.offset = (self.offset + distance) % TILE_PERIOD
        self.strip.local_pos = Vec2(-self.offset, 0)
