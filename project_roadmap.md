# Jazz Engine Optimization & Refactoring Roadmap

This living roadmap lists all optimization, refactoring, and clean-up tasks for the Jazz Engine based on the initial project overview. You can use this checklist to track future development progress.

---

## Completed Tasks

- [x] **Refactor Spatial Grid Construction (`jazz/physics/physics.py`)**
  *Implemented a persistent spatial hash grid with fast-path bounds checks and incremental cell updates to eliminate per-frame reconstruction overhead.*
- [x] **Cache Global Transforms (`jazz/engine/base_object.py`)**
  *Implemented a pull-based caching system for `pos` and `rotation` with recursive dirty flag propagation down the scene graph, eliminating recursive parent queries.*
- [x] **Establish a Unit Testing Framework**
  *Added `unit_tests/test_physics_grid.py` and `unit_tests/test_transforms.py` to assert correctness of grid mappings and coordinate transforms in headless environments.*
- [x] **Consolidate and Unify UI Systems (`jazz/user_interface.py` vs `jazz/components/*`)**
  *Deprecated `user_interface.py` and migrated components (including `TextBox` and containers `VBox`, `HBox`, `UIContainer`) into `components/` using the event-driven entity-component architecture.*
- [x] **Optimize Separating Axis Theorem (SAT) Collisions (`jazz/physics/colliders.py`)**
  *Pre-calculated and cached normal vectors, updating them only when the parent object's rotation changes.*
- [x] **Active Area Collision Check (`jazz/physics/area.py`)**
  *Only check collisions against objects whose bounding boxes have moved in the current frame.*
- [x] **Collision Resolution Phase (`jazz/physics/body.py`)**
  *Calculate penetrations first and apply corrections simultaneously to avoid multi-body tunneling.*
- [x] **Squared-Distance Raycasts (`jazz/physics/ray.py`)**
  *Use `magnitude_squared()` to compare distances instead of `dist_to` (which calls slow square-root routines).*
- [x] **Integer Mask Layers (`jazz/physics/_physics_object.py`)**
  *Convert mask layers (e.g. `"0001"`) into integers to perform instantaneous bitwise AND `&` comparisons.*

---

## Top Priority Tasks (Next Up)

- [ ] **Implement Object Pool for Particles (`jazz/_in_dev/particles.py`)**
  - **Problem**: Frequent allocation and garbage collection of `Particle` dataclasses triggers engine stutter.
  - **Proposed Solution**: Pre-allocate a particle array pool and recycle dead particles.

---

## Module-by-Module Improvements

### Core Module

- [ ] **Viewport and View Cache (`jazz/camera.py`)**
  - Cache display dimensions (`Globals.display.get_width()` / `height`) on window resize to avoid calling them every frame.
  - Adjust screen shake algorithm to avoid single-frame jumps.
- [ ] **Decouple Engine Settings (`jazz/global_dict.py`)**
  - Pass a `Context` or `Engine` object down the scene graph (or use dependency injection) instead of relying on the global mutable `Globals` singleton.
- [ ] **Consolidate Drawing Targets (`jazz/primatives.py`)**
  - Clean up hardware-vs-software checking loops. Fully commit to `_sdl2` rendering targets.
- [ ] **Vector Allocation Cleanup (`jazz/utils.py`)**
  - Use in-place vector operations (e.g. `vec.normalize_ip()`) to reduce `pygame.Vector2` object creation overhead in math loops.

---

### Engine Module

- [ ] **Delta Time Configuration (`jazz/engine/application.py`)**
  - Expose `max_frame_time` (currently hardcoded to `1/15`) in `SETTINGS` to allow custom frame-step tuning.
- [ ] **Set-based Group Lookup (`jazz/engine/group.py`)**
  - Replace internal list representation with a `set` for O(1) insertion, deletion, and membership checking.
- [ ] **Single-Pass Event Polling (`jazz/engine/input_handler.py`)**
  - Query the event queue `pygame.event.get()` exactly once per frame and dispatch inputs.
- [ ] **Resource Release & Reference Counting (`jazz/engine/resource_manager.py`)**
  - Implement weak references (`weakref`) or an `unload_unused()` method to prevent RAM/VRAM leaks on scene unload.
- [ ] **Dynamic Physics Layers (`jazz/engine/scene.py`)**
  - Make the number of physics grid layers configurable instead of hardcoded to four layers (0-3).
- [ ] **Audio Initialization Decoupling (`jazz/engine/sound_manager.py`)**
  - Accept settings as an initialization volume dict rather than hardcoding dependency on `SETTINGS["AUDIO"]`.

---

### Component Features

- [ ] **DRY Sprite Sheet Parsing (`jazz/components/animated_sprite.py`)**
  - Extract repetitive spritesheet parser logic into a common helper function.
- [ ] **Event-driven UI Actions (`jazz/components/button.py`)**
  - Remove button-state updates from the global polling loop. Trigger actions directly when events are processed.
- [ ] **Lazy Font Texture Rendering (`jazz/components/label.py`)**
  - Lazily re-render text surfaces only right before rendering if marked dirty, rather than immediately on set.
- [ ] **Direct Geometry Progress Bar (`jazz/components/progress_bar.py`)**
  - Render health/progress bars using standard geometry primitive draws rather than creating/recreating text surfaces.
- [ ] **Bounding Box Cache (`jazz/components/sprite.py`)**
  - Cache the `pygame.Rect` object on `Sprite` and update it only when `pos`, `scale`, or size changes.

---

### Physics Module

*All tasks completed.*

---

### Animation & Time Module

- [ ] **Interpret Math DECIMALS (`jazz/animation/easing.py`)**
  - Replace literal fraction math with decimals (e.g., use `0.5` instead of `/ 2`) to avoid interpreter overhead and clean up legacy commented JS remnants.
- [ ] **Timer IDs (`jazz/animation/timer.py`)**
  - Replace the heavy `uuid.uuid1()` generator with built-in `id()` or an incrementing integer counter.
- [ ] **Tween Setter Reference (`jazz/animation/tween.py`)**
  - Accept a direct setter function reference or a dictionary key instead of string-based `setattr`/`getattr` reflection.
