"""The player's bird: an Area sensor with a circle collider and a flapping AnimatedSprite."""

from jazz import COLLIDER_CIRCLE, AnimatedSprite, Area, Vec2

from config import FLAP_VELOCITY, GRAVITY, LAYER_NONE, MAX_FALL_SPEED, PIXEL_SCALE, Z_BIRD, asset, play_sound

RADIUS = 14
TILT_UP = -25.0
TILT_DOWN = 90.0
# Fall speed at which the bird starts to nose-dive
DIVE_SPEED = 250.0


class Bird(Area):
    """Player bird that falls under gravity, flaps upward and senses pipes, ground and score gates."""

    def __init__(self, **kwargs) -> None:
        """Initializes the Bird.

        Args:
            pos (tuple | Vec2, optional): Starting position. Defaults to (0, 0).
            flapping (bool, optional): Starts the wing animation. Defaults to True.
        """
        kwargs.setdefault("name", "Bird")
        kwargs.setdefault("z", Z_BIRD)
        kwargs.setdefault("layers", LAYER_NONE)
        # Senses both the obstacle and the score gate layers
        kwargs.setdefault("collision_layers", "0011")
        super().__init__(**kwargs)
        self.velocity: float = 0.0
        self.tilt: float = 0.0
        self.alive: bool = True
        self.add_collider(COLLIDER_CIRCLE, radius=RADIUS)
        self.sprite: AnimatedSprite = self.add_child(
            AnimatedSprite(
                spritesheet=asset("bird.png"),
                sprite_dim=(19, 14),
                animation_frames=[0, 1, 2, 1],
                animation_fps=12,
                playing=kwargs.get("flapping", True),
                scale=(PIXEL_SCALE, PIXEL_SCALE),
                anchor=("center", "center"),
            )
        )

    def flap(self) -> None:
        """Launches the bird upward and plays the flap sound."""
        self.velocity = FLAP_VELOCITY
        play_sound("flap")

    def fall(self, delta: float, floor: float | None = None) -> bool:
        """Applies gravity, moves the bird and updates its tilt.

        Args:
            delta (float): Time in seconds since the last frame.
            floor (float | None, optional): Y position the bird's centre can't fall below. Defaults to None.

        Returns:
            bool: True if the bird is resting on the floor.
        """
        self.velocity = min(self.velocity + GRAVITY * delta, MAX_FALL_SPEED)
        new_pos = self.pos + Vec2(0, self.velocity * delta)
        landed = False
        if floor is not None and new_pos.y >= floor:
            new_pos.y = floor
            self.velocity = 0.0
            landed = True
        self.pos = new_pos

        if self.velocity < DIVE_SPEED and not landed:
            target = TILT_UP
            rate = 600.0
        else:
            target = TILT_DOWN
            rate = 360.0
        if self.tilt < target:
            self.tilt = min(target, self.tilt + rate * delta)
        else:
            self.tilt = max(target, self.tilt - rate * delta)
        self.set_tilt(self.tilt)
        return landed

    def set_tilt(self, degrees: float) -> None:
        """Rotates the bird's sprite. Positive angles tip the beak down.

        The sprite is rotated rather than the Area so the collider keeps its
        orientation.

        Args:
            degrees (float): Tilt in degrees, clockwise on screen.
        """
        self.tilt = degrees
        self.sprite.rotation = degrees

    def die(self) -> None:
        """Marks the bird dead and freezes its wings."""
        self.alive = False
        self.sprite.stop()
