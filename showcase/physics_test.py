import random
import math
import pygame
from base import Test
import jazz
from jazz import (
    Globals,
    Vec2,
    Color,
    Surface,
    Draw,
    Body,
    Label,
    Button,
    Sprite,
    VBox,
    HBox,
    COLLIDER_RECT,
    COLLIDER_CIRCLE,
    COLLIDER_POLY,
)
from jazz._in_dev._in_dev import DynamicBody


def make_regular_polygon(sides: int, radius: float) -> list[Vec2]:
    """Generates local vertices for a regular convex polygon centered at origin.

    Args:
        sides (int): Number of sides of the polygon.
        radius (float): The distance from origin to vertices.

    Returns:
        list[Vec2]: List of vertices.
    """
    verts = []
    for i in range(sides):
        angle = i * (2 * math.pi / sides) - math.pi / 2
        verts.append(Vec2(radius * math.cos(angle), radius * math.sin(angle)))
    return verts


def generate_circle_texture() -> Surface:
    """Generates a high-quality 256x256 circle texture with a neon pink/purple gradient and a rotation indicator."""
    surf = Surface((256, 256), pygame.SRCALPHA)
    center = (128, 128)
    max_r = 127
    
    # Draw radial gradient
    for r in range(max_r, 0, -1):
        t = r / max_r
        color = (
            int(255 * t + 75 * (1 - t)),
            0,
            int(128 * t + 130 * (1 - t)),
            255
        )
        pygame.draw.circle(surf, color, center, r)
        
    # Draw outer neon ring
    pygame.draw.circle(surf, (255, 255, 255, 255), center, max_r, width=3)
    pygame.draw.circle(surf, (255, 105, 180, 150), center, max_r - 2, width=2)
    
    # Draw rotation indicators (spokes)
    pygame.draw.line(surf, (255, 255, 255, 220), center, (128, 128 - max_r), 3)
    pygame.draw.line(surf, (255, 255, 255, 100), center, (128 + max_r, 128), 2)
    pygame.draw.line(surf, (255, 255, 255, 100), center, (128, 128 + max_r), 2)
    pygame.draw.line(surf, (255, 255, 255, 100), center, (128 - max_r, 128), 2)
    
    # Glassy shine reflection
    pygame.draw.circle(surf, (255, 255, 255, 80), (90, 90), 25)
    pygame.draw.circle(surf, (255, 255, 255, 40), (95, 95), 15)
    
    return surf


def generate_rect_texture() -> Surface:
    """Generates a high-quality 256x256 rounded rect texture with a neon cyan/blue gradient."""
    surf = Surface((256, 256), pygame.SRCALPHA)
    
    # Draw linear gradient from center outwards
    for i in range(127, 0, -2):
        t = i / 127.0
        color = (
            int(0 * t + 10 * (1 - t)),
            int(255 * t + 20 * (1 - t)),
            int(255 * t + 60 * (1 - t)),
            255
        )
        w = int(254 * t)
        h = int(254 * t)
        x = 128 - w // 2
        y = 128 - h // 2
        r = max(4, int(24 * t))
        pygame.draw.rect(surf, color, (x, y, w, h), border_radius=r)
        
    # Outer borders
    pygame.draw.rect(surf, (255, 255, 255, 255), (1, 1, 254, 254), width=3, border_radius=24)
    pygame.draw.rect(surf, (0, 191, 255, 150), (3, 3, 250, 250), width=2, border_radius=22)
        
    return surf


def generate_poly_texture(sides: int) -> Surface:
    """Generates a high-quality 256x256 regular polygon texture of given sides with gradient fill."""
    surf = Surface((256, 256), pygame.SRCALPHA)
    center = (128, 128)
    max_r = 127
    
    # Colors depending on sides
    if sides == 3:
        c_start = (57, 255, 20)
        c_end = (5, 45, 10)
        border_col = (124, 252, 0)
    elif sides == 5:
        c_start = (255, 255, 0)
        c_end = (80, 20, 0)
        border_col = (255, 165, 0)
    else:
        c_start = (255, 0, 255)
        c_end = (40, 0, 40)
        border_col = (238, 130, 238)
        
    # Draw concentric scaled polygons to create a gradient
    for r in range(max_r, 0, -4):
        t = r / max_r
        color = (
            int(c_start[0] * t + c_end[0] * (1 - t)),
            int(c_start[1] * t + c_end[1] * (1 - t)),
            int(c_start[2] * t + c_end[2] * (1 - t)),
            255
        )
        points = []
        for i in range(sides):
            angle = i * (2 * math.pi / sides) - math.pi / 2
            points.append((128 + r * math.cos(angle), 128 + r * math.sin(angle)))
        pygame.draw.polygon(surf, color, points)
        
    # Outer white/accent border
    outer_points = []
    for i in range(sides):
        angle = i * (2 * math.pi / sides) - math.pi / 2
        outer_points.append((128 + max_r * math.cos(angle), 128 + max_r * math.sin(angle)))
    pygame.draw.polygon(surf, (255, 255, 255, 255), outer_points, width=3)
    pygame.draw.polygon(surf, border_col + (150,), outer_points, width=1)
    
    # Draw internal structure lines (spokes from center to vertices)
    for pt in outer_points:
        pygame.draw.line(surf, (255, 255, 255, 50), center, pt, 1)
        
    return surf




class PhysicsTest(Test):
    """Showcase and stress test scene for the 2D physics engine."""

    name = "Physics Test"

    def __init__(self) -> None:
        """Initializes the PhysicsTest scene and simulation state variables."""
        super().__init__()
        self.gravity_enabled = True
        self.gravity_accel = 500.0
        self.grid_overlay = True
        self.dynamic_bodies = []
        self.static_bodies = []
        self.dragged_object = None
        self.drag_offset = Vec2()
        self.prev_mouse_pos = Vec2()
        self.throw_velocity = Vec2()
        self.ray_start = Vec2(400, 160)
        self.selected_body = None

        # UI elements
        self.fps_label = None
        self.stats_label = None
        self.controls_label = None
        self.selected_label = None
        self.btn_gravity = None
        self.btn_debug = None
        self.btn_grid = None
        self.btn_clear = None
        self.btn_spawn = None

        # Fixed obstacles references
        self.center_circle = None
        self.spinner = None

    def on_load(self, data: dict) -> None:
        """Creates boundaries, rotated obstacles, HUD text, buttons, and enables debug wireframe by default.

        Args:
            data (dict): State transfer data from previous scene.
        """
        super().on_load(data)
        self._debug = True  # Enable debug colliders rendering by default

        # Generate and register shape textures
        circle_surf = generate_circle_texture()
        rect_surf = generate_rect_texture()
        poly_3_surf = generate_poly_texture(3)
        poly_5_surf = generate_poly_texture(5)

        Globals.resource.add_texture(circle_surf, "circle_texture")
        Globals.resource.add_texture(rect_surf, "rect_texture")
        Globals.resource.add_texture(poly_3_surf, "poly_3_texture")
        Globals.resource.add_texture(poly_5_surf, "poly_5_texture")

        # 1. Create walls enclosing the physics area (Y: 130 to 780, X: 20 to 780)
        self.create_wall(Vec2(400, 130), 800, 10)  # Top boundary
        self.create_wall(Vec2(400, 785), 800, 10)  # Bottom floor
        self.create_wall(Vec2(10, 455), 20, 650)   # Left wall
        self.create_wall(Vec2(790, 455), 20, 650)  # Right wall

        # 2. Create static slanted ramps and obstacles
        self.create_obstacle(Vec2(230, 310), 180, 20, rotation=25)
        self.create_obstacle(Vec2(570, 310), 180, 20, rotation=-25)

        # Rotating circle in center
        self.center_circle = self.create_obstacle(Vec2(400, 480), 80, 80, is_circle=True)

        # Sweeper spinner bar
        self.spinner = self.create_obstacle(Vec2(400, 640), 220, 15, rotation=0)

        ui = self.add_object(HBox(pos=(0, 0), size=(800, 125), align="top", padding=0, bg_color=(64, 64, 64, 100), radius=0, shadow_offset=(0,0), shadow_blur=0, spacing=0))
        left_column = ui.add_child(VBox(align="left", auto_size=True, spacing=10))
        right_column = ui.add_child(VBox(align="left", auto_size=True, spacing=0))

        # 3. Create UI Labels in the top control panel
        self.fps_label = right_column.add_child(
            Label(text="FPS: --", anchor=(0, 0), fontsize=18)
        )
        self.stats_label = right_column.add_child(
            Label(text="Bodies: 0 | Cells: 0", anchor=(0, 0), fontsize=18)
        )
        self.controls_label = right_column.add_child(
            Label(
                text="Keys: [D] Debug [G] Gravity [H] Grid [C] Clear [R] Random",
                anchor=(0, 0),
                fontsize=14,
                text_color=(200, 200, 200),
            )
        )
        right_column.add_child(
            Label(
                text="Click empty space to spawn dynamic shapes. Drag & throw shapes with left click.",
                anchor=(0, 0),
                fontsize=14,
                text_color=(200, 200, 200),
            )
        )
        self.selected_label = right_column.add_child(
            Label(
                text="Selected: None (Right-click a body to inspect)",
                anchor=(0, 0),
                fontsize=14,
                text_color=(255, 255, 100),
            )
        )

        # 4. Create UI Control Buttons
        row1 = HBox(padding=0)
        row1.add_child(Button(size=(130, 25), anchor=(1, 0), label="Toggle Gravity", text_size=12, callback=self.toggle_gravity))
        row1.add_child(Button(size=(130, 25), anchor=(1, 0), label="Toggle Debug", text_size=12, callback=self.toggle_debug_mode))
        left_column.add_child(row1)

        row2 = HBox(padding=0)
        row2.add_child(Button(size=(130, 25), anchor=(1, 0), label="Toggle Grid", text_size=12, callback=self.toggle_grid))
        row2.add_child(Button(size=(130, 25), anchor=(1, 0), label="Clear Bodies", text_size=12, callback=self.clear_dynamic))
        left_column.add_child(row2)

        row3 = HBox(padding=0)
        row3.add_child(Button(size=(130, 25), anchor=(1, 0), label="Spawn 50 Random", text_size=12, callback=self.spawn_50_random))

        left_column.add_child(row3)


    def create_wall(self, pos: Vec2, w: float | int, h: float | int) -> Body:
        """Helper to spawn a static boundary wall.

        Args:
            pos (Vec2): Center coordinates.
            w (float | int): Width of the wall.
            h (float | int): Height of the wall.

        Returns:
            Body: The created static body.
        """
        wall = Body(static=True, pos=pos)
        wall.add_collider(COLLIDER_RECT, w=w, h=h)
        wall.add_child(Sprite(texture=Globals.resource.get_color(Color(128,128,128,255)), scale=(w,h), anchor=(0.5,0.5)))

        self.add_object(wall)
        self.static_bodies.append(wall)
        return wall

    def create_obstacle(self, pos: Vec2, w: float | int, h: float | int, rotation: float = 0, is_circle: bool = False) -> Body:
        """Helper to spawn static obstacles and attach scaled sprites to match their shapes.

        Args:
            pos (Vec2): Center coordinates.
            w (float | int): Width of the obstacle.
            h (float | int): Height of the obstacle.
            rotation (float, optional): Initial rotation angle in degrees. Defaults to 0.
            is_circle (bool, optional): Whether this is a circular obstacle. Defaults to False.

        Returns:
            Body: The created static body.
        """
        obs = Body(static=True, pos=pos, rotation=rotation)
        if is_circle:
            obs.add_collider(COLLIDER_CIRCLE, radius=w / 2)
            obs.add_child(Sprite(texture="circle_texture", scale=(w / 256, w / 256), anchor=(0.5, 0.5)))
        else:
            obs.add_collider(COLLIDER_RECT, w=w, h=h)
            obs.add_child(Sprite(texture="rect_texture", scale=(w / 256, h / 256), anchor=(0.5, 0.5)))
        self.add_object(obs)
        self.static_bodies.append(obs)
        return obs

    def update(self, delta: float) -> None:
        """Updates rotating elements, handles inputs, and prunes dead bodies.

        Args:
            delta (float): Time since the last frame.
        """
        # Rotate static center circle and spinner sweeper
        if self.center_circle:
            self.center_circle.rotate(20 * delta)
        if self.spinner:
            self.spinner.rotate(-45 * delta)

        # Handle mouse dragging, throwing, and spawning
        self.handle_mouse_input(delta)

        # Handle keyboard shortcuts
        self.handle_keyboard_input()

        # Prune killed dynamic bodies
        self.dynamic_bodies = [b for b in self.dynamic_bodies if not b.do_kill]

    def late_update(self, delta: float) -> None:
        """Updates text labels for stats, FPS, and instructions.

        Args:
            delta (float): Time since the last frame.
        """
        super().late_update(delta)

        # Refresh stats
        self.fps_label.set_text(f"FPS: {Globals.app.get_fps():2.2f}")

        # Sum occupied cells across all layers
        cells_count = sum(len(layer_grid.grid) for layer_grid in self._physics_world.values())
        total_bodies = len(self.dynamic_bodies) + len(self.static_bodies)
        self.stats_label.set_text(
            f"Bodies: {total_bodies} (Dyn: {len(self.dynamic_bodies)}, Stat: {len(self.static_bodies)}) | Grid Cells: {cells_count}"
        )

        gravity_text = f"ON ({self.gravity_accel} px/s^2)" if self.gravity_enabled else "OFF"
        self.controls_label.set_text(
            f"Gravity: {gravity_text} | Keys: [D] Debug [G] Gravity [H] Grid [C] Clear [R] Random"
        )

        # Update selected body info
        if self.selected_body is not None and not getattr(self.selected_body, "do_kill", False):
            pos = self.selected_body.pos
            vel = getattr(self.selected_body, "velocity", Vec2(0, 0))
            if hasattr(self.selected_body, "on_ground"):
                self.selected_label.set_text(
                    f"Selected: {self.selected_body.name} | Pos: ({pos.x:3.1f}, {pos.y:3.1f}) | Vel: ({vel.x:3.1f}, {vel.y:3.1f}) | Grounded: {self.selected_body.on_ground}"
                )
            else:
                self.selected_label.set_text(
                    f"Selected: {self.selected_body.name} | Pos: ({pos.x:3.1f}, {pos.y:3.1f}) | Vel: ({vel.x:3.1f}, {vel.y:3.1f})"
                )
        else:
            self.selected_body = None
            self.selected_label.set_text("Selected: None (Right-click a body to inspect)")

    def handle_mouse_input(self, delta: float) -> None:
        """Manages clicking empty space to spawn, clicking dynamic bodies to drag & throw, and tracking mouse velocities.

        Args:
            delta (float): Time since the last frame.
        """
        mouse_pos = Globals.mouse.pos

        # Track mouse frame-to-frame delta to compute throwing velocity
        if delta > 0:
            self.throw_velocity = (mouse_pos - self.prev_mouse_pos) / delta
        self.prev_mouse_pos = mouse_pos

        if Globals.mouse.click("left"):
            # Check if clicked on an existing dynamic body
            clicked_body = None
            for b in self.dynamic_bodies:
                rect = b.collider.get_rect()
                if rect.collidepoint(mouse_pos.x, mouse_pos.y):
                    clicked_body = b
                    break

            if clicked_body is not None:
                self.dragged_object = clicked_body
                self.drag_offset = clicked_body.pos - mouse_pos
                self.dragged_object.on_ground = False
            else:
                # Clicked empty space: Spawn a shape if click is inside active sandbox (Y > 135)
                if mouse_pos.y > 135 and 20 < mouse_pos.x < 780:
                    self.spawn_random_shape(mouse_pos)

        elif Globals.mouse.held("left") and self.dragged_object is not None:
            # Drag object and update its velocity continuously
            self.dragged_object.pos = mouse_pos + self.drag_offset
            self.dragged_object.velocity = self.throw_velocity
            self.dragged_object.on_ground = False

        else:
            self.dragged_object = None

        # Right click to select a body (dynamic or static)
        if Globals.mouse.click("right"):
            clicked_body = None
            for b in self.dynamic_bodies + self.static_bodies:
                rect = b.collider.get_rect()
                if rect.collidepoint(mouse_pos.x, mouse_pos.y):
                    clicked_body = b
                    break
            self.selected_body = clicked_body

    def handle_keyboard_input(self) -> None:
        """Processes keyboard shortcuts for debugging toggles, gravity, clearing, and random spawning."""
        if Globals.key.press("d"):
            self.toggle_debug_mode()
        if Globals.key.press("g"):
            self.toggle_gravity()
        if Globals.key.press("h"):
            self.toggle_grid()
        if Globals.key.press("c"):
            self.clear_dynamic()
        if Globals.key.press("r"):
            self.spawn_50_random()

    def spawn_random_shape(self, pos: Vec2) -> None:
        """Spawns a random circle, rectangle, or polygon with random velocity, restitution, and scaled shape textures.

        Args:
            pos (Vec2): Position to spawn the shape at.
        """
        shape_type = random.choice(["circle", "rect", "poly"])
        size = random.randint(15, 30)
        vel = Vec2(random.uniform(-150, 150), random.uniform(-50, 50))
        restitution = random.uniform(0.4, 0.7)

        body = DynamicBody(pos=pos, velocity=vel, restitution=restitution)
        if shape_type == "circle":
            body.add_collider(COLLIDER_CIRCLE, radius=size)
            body.add_child(Sprite(texture="circle_texture", scale=(size / 128, size / 128), anchor=(0.5, 0.5)))
        elif shape_type == "rect":
            body.add_collider(COLLIDER_RECT, w=size * 2, h=size * 2)
            body.add_child(Sprite(texture="rect_texture", scale=(size / 128, size / 128), anchor=(0.5, 0.5)))
        else:
            sides = random.choice([3, 5])
            verts = make_regular_polygon(sides, size * 1.2)
            body.add_collider(COLLIDER_POLY, vertices=verts)
            scale_val = (size * 1.2) / 128.0
            body.add_child(Sprite(texture=f"poly_{sides}_texture", scale=(scale_val, scale_val), anchor=(0.5, 0.5)))

        self.add_object(body)
        self.dynamic_bodies.append(body)

    def toggle_gravity(self) -> None:
        """Toggles gravity acceleration simulation."""
        self.gravity_enabled = not self.gravity_enabled

    def toggle_debug_mode(self) -> None:
        """Toggles debug lines rendering for colliders."""
        self.toggle_debug()

    def toggle_grid(self) -> None:
        """Toggles spatial hash grid cells visual overlay."""
        self.grid_overlay = not self.grid_overlay

    def clear_dynamic(self) -> None:
        """Removes all dynamic shapes from the scene."""
        for b in self.dynamic_bodies:
            b.queue_kill()
        self.dynamic_bodies.clear()

    def spawn_50_random(self) -> None:
        """Spawns 50 random shapes in the upper region of the sandbox."""
        for _ in range(50):
            pos = Vec2(random.randint(50, 750), random.randint(140, 250))
            self.spawn_random_shape(pos)

    def render(self) -> None:
        """Draws visual spatial hash cells, panel divider, and raycast visualization overlays."""
        # 1. Clear the screen manually
        Globals.renderer.draw_color = self.camera._bg_color
        Globals.renderer.clear()

        # 2. Draw spatial grid partition overlay (behind sprites)
        if self.grid_overlay:
            grid_size = 50
            grid_color = Color(35, 35, 35)
            # Draw vertical lines
            for x in range(0, 800, grid_size):
                Draw.line(Vec2(x, 130), Vec2(x, 780), grid_color, 1)
            # Draw horizontal lines
            for y in range(130, 780, grid_size):
                Draw.line(Vec2(20, y), Vec2(780, y), grid_color, 1)

        # 3. Render the sprites (without clearing the screen again)
        prev_blanking = self.camera._blanking
        self.camera._blanking = False
        try:
            super().render()
        finally:
            self.camera._blanking = prev_blanking

        # 4. Draw remaining overlays on top of the sprites
        # Dynamic mouse-based raycast demo
        mouse_pos = Globals.mouse.pos
        if mouse_pos.y > 130:
            blacklist = self.static_bodies + ([self.dragged_object] if self.dragged_object else [])
            hit_obj, hit_pos = self.physics_raycast(self.ray_start, mouse_pos, blacklist=blacklist)

            # Draw laser emitter base
            Draw.fill_circle(self.ray_start, 6, Color("yellow"))
            Draw.circle(self.ray_start, 10, Color("orange"), 1)

            if hit_pos is not None:
                # Laser is blocked: Draw green segment to hit, red beyond it to mouse
                Draw.line(self.ray_start, hit_pos, Color("green"), 2)
                Draw.line(hit_pos, mouse_pos, Color("red"), 1)
                # Render hit pointer
                Draw.fill_circle(hit_pos, 5, Color("red"))
                Draw.circle(hit_pos, 8, Color("red"), 1)
            else:
                # Clear path: Draw fully green ray line to mouse
                Draw.line(self.ray_start, mouse_pos, Color("green"), 2)

        # Horizontal panel boundary line
        Draw.line(Vec2(0, 130), Vec2(800, 130), Color("gray"), 3)

        # Highlight selected body
        if self.selected_body is not None and not getattr(self.selected_body, "do_kill", False):
            rect = self.selected_body.collider.get_rect()
            Draw.rect(rect, Color("yellow"), 2)
            # Draw.circle(self.selected_body.pos, 4, Color("yellow"), 1)


if __name__ == "__main__":
    from jazz import Application
    app = Application(800, 800)
    app.add_scene(PhysicsTest)
    app.run()
