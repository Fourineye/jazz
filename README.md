# Engine
This project wraps pygame into a more convenient format that handles some of the more common tasks in game development.


## Architecture & Structure Overview

The Jazz Engine is built around a nested scene-graph hierarchy using the entity-component layout pattern. The engine coordinates execution flow via several core modules:

1. **Application (`jazz.Application`)**: Handles the global lifecycle, initializes SDL2/Pygame contexts, manages display surfaces, and runs the main loop with delta time calculation.
2. **Globals & Context (`jazz.Globals`)**: Exposes engine singletons such as renderer, active input handlers, resource manager, and sound systems for centralized access.
3. **Scene graph (`jazz.Scene`)**: Manages the hierarchy of loaded game objects. All game objects are updated and rendered in a depth-first traversal of the scene graph.
4. **Resources (`jazz.ResourceManager`)**: Caches and manages images, textures, fonts, and sprite sheets, ensuring memory is optimized.
5. **Sounds (`jazz.SoundManager`)**: Manages channels, volume, music playing/fading, and sound effect loading.

---

## Component Extensibility

All entities in the Jazz Engine extend the `jazz.GameObject` class. Game objects support child nesting, meaning child offsets automatically propagate based on parent transformations.

### Custom Component Lifecycle

When extending `GameObject`, you override three primary life-cycle methods:
- `on_load(self)`: Executed once when the object is instantiated and mounted to the active scene graph. Ideal for loading sprites, adding colliders, or registering event listeners.
- `update(self, delta: float)`: Executed once per frame. Use this to handle custom logic, compute movement, or check input states.
- `late_update(self, delta: float)`: Executed after all objects in the scene graph have completed their `update()` call. Ideal for tracking cameras or finalizing relative offsets.

### Built-in Extensible Components

The engine provides several components that can be customized or subclassed under `jazz.components`:
- `Sprite`: Manages anchor alignment, hardware/software drawing offsets, scale, alpha transparency, and rendering.
- `AnimatedSprite`: Extends sprite rendering to handle sheet frame playback, custom frames per second (fps), and animations.
- `Button` & `TextBox`: Handle inputs, cursor focus, active states, text rendering, and events dynamically.
- `Label` & `ProgressBar`: Provide modular UI components to render text layouts and value representations.
- `VBox` & `HBox`: Container components that layout UI children vertically or horizontally.

---

## 2D Physics Subsystem

The physics system is designed to provide responsive spatial checks and rigid collisions. It is divided into three key elements:

### 1. Spatial Partitioning (`PhysicsGrid`)
To avoid checking collisions between every object in a scene (an O(N^2) operation), the engine maintains a `PhysicsGrid`.
- It dynamically partitions the scene into cell blocks.
- On updates, objects register their axis-aligned bounding boxes (AABB) with the cells they overlap.
- Collision checks are only conducted between objects that share active grid cells, reducing candidate comparisons to O(N).

### 2. Colliders & SAT Math (`Collider`)
The engine defines collision shapes extending from the base `Collider`:
- `RectCollider`: Defined by axis-aligned bounds.
- `CircleCollider`: Defined by a radius.
- `PolyCollider`: Defined by an arbitrary convex hull polygon.
- `RayCollider`: Defined by a line segment.

Precise collisions are resolved using the **Separating Axis Theorem (SAT)**. SAT projects shape vertices onto potential separating axes (face normals). If all projections overlap, the shapes are colliding, and the algorithm returns:
- The minimum **penetration depth** needed to separate the shapes.
- The **collision normal** indicating the direction of penetration.

### 3. Bodies vs. Areas (`PhysicsObject`)
Active physical objects inherit from `PhysicsObject` and are implemented in two forms:
- **`Body`**: Represents solid, physical entities. When a `Body` moves via `move_and_collide(direction)`, it queries the grid for overlapping objects. If a collision occurs, it calculates the SAT penetration and instantly corrects positions based on whether the obstacles are static or dynamic.
- **`Area`**: Represents sensor zones (e.g. triggers, detection fields). Instead of resolving physical responses, an `Area` queries overlapping objects using `get_entered()` to trigger event callbacks.

### 4. Collision Mask Filtering
Collision layers are configured using binary representation (or integer masks). Objects will only collide if a bitwise AND comparison matches between their layers and the collision mask of the target:
`is_matching = (self.layers & target.collision_layers) != 0`

## Basic Example Program
```py
import jazz


class Player(jazz.GameObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "Player")
        super().__init__(**kwargs)
        self.add_child(jazz.Sprite())

    def update(self, delta: float):
        movement = jazz.Vec2()
        if jazz.GAME_GLOBALS["Key"].held("up"):
            movement.y -= 1
        if jazz.GAME_GLOBALS["Key"].held("down"):
            movement.y += 1
        if jazz.GAME_GLOBALS["Key"].held("left"):
            movement.x -= 1
        if jazz.GAME_GLOBALS["Key"].held("right"):
            movement.x += 1

        self.move(movement * 100 * delta)


class MainScene(jazz.Scene):
    name = "Main"
    def on_load(self, data):
        self.add_object(Player(pos=(100, 100)), "player")

    def update(self, delta: float):
        jazz.GAME_GLOBALS["App"].set_caption(self.player.pos)


if __name__ == "__main__":
    app = jazz.Application(800, 600)
    app.add_scene(MainScene)
    app.run()

```