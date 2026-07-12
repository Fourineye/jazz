from ..global_dict import Globals
from ..components import Label, Sprite, TextBox
from ..utils import Color, Rect, Surface, Vec2
from ..physics import Body


# class CheckBox(Sprite):
#     def __init__(self, name="CheckBox", **kwargs):
#         source = Surface((16, 16))
#         source.fill((10, 10, 25))
#         pygame.draw.circle(source, (20, 20, 40), (7, 7), 8)
#         pygame.draw.rect(source, (128, 128, 128), (0, 0, 16, 16), 1)
#         super().__init__(name, asset=source, **kwargs)
#         self._checkmark = jazz.Surface((24, 16))
#         pygame.draw.lines(
#             self._checkmark, (64, 128, 64), False, ((0, 8), (8, 16), (16, 0))
#         )
#         self.checked = False
#
#     def update(self, delta):
#         if self.rect.collidepoint(Globals.mouse.pos):
#             if Globals.mouse.click(0):
#                 self.checked = not self.checked
# 
    # def draw(self, surface, offset=None):
    #     ...


MIN_HORIZONAL_VELOCITY = 1.0
MIN_Y_NORMAL = 0.15
MIN_VERTICAL_VELOCITY = 80.0
GROUND_CAST_DISTANCE = 10


class DynamicBody(Body):
    """Dynamic physical body component that integrates gravity, damping, elastic collision response, and resting sleep states."""

    def __init__(self, velocity: Vec2 | tuple[float, float] | None = None, restitution: float = 0.5, **kwargs) -> None:
        """Initializes the DynamicBody component.

        Args:
            velocity (Vec2 | tuple[float, float] | None, optional): Initial velocity. Defaults to None.
            restitution (float, optional): Elasticity bounce coefficient (0 to 1). Defaults to 0.5.
            **kwargs: Extra arguments passed to base Body component.
        """
        kwargs.setdefault("name", "DynamicBody")
        super().__init__(**kwargs)
        self.velocity = Vec2(velocity or (0, 0))
        self.restitution = restitution
        self.on_ground = False

    def move_and_collide(self, direction: Vec2, _visited: set[str] | None = None) -> list[tuple[Body, tuple[float, Vec2]]]:
        """Moves the dynamic body and wakes it up from resting state if displacement is non-zero.

        Args:
            direction (Vec2): The displacement vector to move along.
            _visited (set[str], optional): Set of object IDs already processed. Defaults to None.

        Returns:
            list[tuple[Body, tuple[float, Vec2]]]: Sensed collision records.
        """
        if direction != Vec2(0, 0):
            self.on_ground = False
        return super().move_and_collide(direction, _visited)

    def update(self, delta: float) -> None:
        """Applies forces, integrates velocity, handles resting/sleep settling, and resolves collisions.

        Args:
            delta (float): Time since the last frame.
        """
        # If resting on ground, verify we are still touching a support surface
        if self.on_ground and not self.static:
            self.move(Vec2(0, GROUND_CAST_DISTANCE))
            collisions = Globals.scene.get_AABB_collisions(self)

            still_on_ground = False
            if collisions:
                for other in collisions:
                    depth, normal = self.collider.collide_sat(other.collider)
                    if depth > 0 and normal.y > MIN_Y_NORMAL:  # other is below us
                        if other.static or getattr(other, "on_ground", False):
                            still_on_ground = True
                            break

            self.move(Vec2(0, -GROUND_CAST_DISTANCE))  # Shift back AFTER precise check
            self.on_ground = still_on_ground
            if self.on_ground:
                self.velocity.y = 0
                if abs(self.velocity.x) < MIN_HORIZONAL_VELOCITY:
                    self.velocity.x = 0

        # Apply gravity if enabled in the scene
        if getattr(Globals.scene, "gravity_enabled", True) and not (self.static or self.on_ground):
            self.velocity.y += getattr(Globals.scene, "gravity_accel", 500.0) * delta

        # Apply basic air resistance damping
        self.velocity *= 0.995

        if not self.static:
            # Move and resolve collisions
            collisions = self.move_and_collide(self.velocity * delta)
            if collisions:
                for other, (depth, normal) in collisions:
                    # Resolve velocity reflection
                    vel_dot_normal = self.velocity.dot(normal)
                    if vel_dot_normal > 0:
                        # Reflect along normal with restitution
                        self.velocity -= normal * (1 + self.restitution) * vel_dot_normal

                # Check if we should settle to ground
                for other, (depth, normal) in collisions:
                    if normal.y > MIN_Y_NORMAL:  # other is below us
                        if other.static or getattr(other, "on_ground", False):
                            if abs(self.velocity.y) < MIN_VERTICAL_VELOCITY:
                                self.on_ground = True
                                self.velocity.y = 0
                                if abs(self.velocity.x) < MIN_HORIZONAL_VELOCITY:
                                    self.velocity.x = 0
                                break

        # Delete if fell way off screen
        if self.pos.y > 850:
            self.queue_kill()
