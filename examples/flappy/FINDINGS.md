# Engine Findings

Engine issues found while building the Flappy Bird example, checked against jazz 1.2.0 at commit `9cf9d4d`.

## 1. `Group.add()` crashes on every GameObject

- **Where:** `jazz/engine/group.py`, `Group.add` / `Group.remove`
- **What:** `add()` reads `entity.groups` and calls `entity.add_group(self)`, but `GameObject` has neither. `BaseObject.__getattr__` raises `AttributeError: 'GameObject' object has no attribute 'groups'`. `remove()` has the same problem.
- **Impact:** `Group` can't hold anything, so `Area(target_group=...)` can't be used either. `Group` is also missing from the top-level `jazz` exports (it's only in `jazz.engine`).
- **Repro:**
  ```python
  from jazz.engine.group import Group
  from jazz import GameObject
  Group().add(GameObject())  # AttributeError
  ```

## 2. `alpha` is ignored for Sprites backed by a plain `Texture`

- **Where:** `jazz/components/sprite.py`, `Sprite.render`
- **What:** The `Image` branch sets `self._texture.alpha = self._alpha` before drawing, but the `Texture` branch never applies alpha. A Sprite loaded from a file path (a `Texture`) with `alpha=0` still draws fully opaque.
- **Impact:** You can't fade sprites loaded from disk (fade-ins, flashes, fading overlays). Sprites using spritesheet frames (`Image`) fade correctly.
- **Fixed:** `Sprite._draw_texture` applies alpha to both kinds, and switches an opaque texture to alpha blending when the sprite is translucent.

## 3. Rotation direction differs between `Texture` and `Image` sprites

- **Where:** `jazz/components/sprite.py`, `Sprite.render` (also `Button.render`)
- **What:** The `Texture` branch passes `self.rotation` to `Texture.draw`, while the `Image` branch sets `Image.angle = -self.rotation`. At `rotation=90`, a Sprite loaded from a file turns clockwise but an `AnimatedSprite` frame turns counter-clockwise.
- **Impact:** The same `rotation` value turns an `AnimatedSprite` the opposite way from a plain `Sprite`.
- **Fixed:** Both kinds now turn clockwise for a positive `rotation`, matching `facing` and the colliders, and both pivot on the anchor point.

## 4. Rotated spritesheet frames show pixels from neighbouring frames

- **Where:** `jazz/engine/resource_manager.py`, `ResourceManager.make_sprite_sheet`
- **What:** Frames are sliced as `Image` sub-regions of one shared texture, with no inset on the sampling area. When a frame is rotated and scaled, SDL's nearest-neighbour sampling can read the texel column just outside the frame, which belongs to the adjacent frame.
- **Impact:** A tightly packed sheet shows thin stray lines along the edges of rotated `AnimatedSprite` frames. Here, the dying bird (rotated to 90°) showed the previous frame's beak column as a line beside its tail. Frames that aren't rotated are unaffected.
- **Suggested engine fix:** Inset the sampling rect slightly, or document that sheets used with rotation need padding between frames.
- **Addressed:** `Image.srcrect` is an integer rect, so a fractional inset isn't possible. `make_sprite_sheet` now documents the problem and takes `spacing` for sheets with gaps between frames.

## Workarounds used in the game

Bugs #2 and #3 are fixed in jazz, and their workarounds were removed. The others are still worked around in the example code:

| Bug | Workaround | Where |
|---|---|---|
| #1 Group | Pipes are tracked in a plain list. Hits are told apart by a custom `kind` property (`properties={"kind": "pipe"}`), not by Group membership. | `scenes/game.py`, `objects/pipes.py` |
| #4 frame bleeding | Each bird frame sits in a 19x14 cell with a 1px transparent border. | `generate_assets.py` `make_bird`, `objects/bird.py` |

## API notes (not bugs, but easy to trip on)

- **`Area.entered` is refreshed in the late update phase (fixed in the engine).** It used to be refreshed in `_engine_update`, before the scene's `update` hook, so objects moved in `Scene.update` were tested at last frame's position and a fast-falling bird was caught ~29px inside the ground. The engine now refreshes it after `Scene.update`. The game moves everything in `update` and reads `bird.entered` in `late_update`. Reading `entered` in `update` still gives last frame's result.
- **`Scene.create_timer` returns `None`**, so a repeating timer made with it can't be cancelled. The game builds a `Timer` itself with `add_object(Timer(...))` so it keeps a reference and can `queue_kill()` it.
- **Every `Scene.__init__` calls `Globals.sound.clear_sounds()`**, which stops any sound still playing. A transition sound played just before switching scenes gets cut off, so the game plays its swoosh from the new scene's `on_load`.
- **`Tween` loops restart from the start value** rather than ping-ponging. A custom easing callable (`sin(2πt)`) makes a looping bob that returns to its start.

## Working correctly

- Nearest-neighbour upscaling: pixel art scaled with `scale=(3, 3)` stays crisp.
- Scene switching and data passing (`set_next_scene` + `stop`, `on_unload` → `on_load`), repeated across menu → game → game over → game/menu.
- Static `Body` rect colliders on one layer and sensor `Area`s on another, queried from a circle-collider `Area` through `collision_layers`. Pipe, ground and score-gate overlaps were all detected correctly.
- Moving a parent `GameObject` carries its child Bodies, Areas and Sprites with it, and the physics grid follows.
- `AnimatedSprite` spritesheet slicing and playback, `Button` with custom textures, `Label`, `Tween` with `EASE_OUT_BACK` and `on_end`, camera shake, `SoundManager`.
- Performance: a steady ~60 FPS (vsync cap) through a scripted playthrough of all three scenes.
