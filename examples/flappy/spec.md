# Flappy Bird on jazz: Spec

A Flappy Bird clone that exercises the jazz engine: scenes, Sprites, AnimatedSprites, the collision system (Areas, Bodies, Groups), UI, Tweens, Timers and the SoundManager.

**Location:** `examples/flappy/`. No changes are made to `jazz/`. If an engine bug or missing feature blocks the game, work stops and the maintainer is asked before any workaround goes in. Every engine issue found is logged in `examples/flappy/FINDINGS.md`.

## Files

| File | Purpose |
|---|---|
| `generate_assets.py` | Standalone script (pygame only, no jazz) that writes every PNG and WAV into `assets/`. Run once. |
| `main.py` | Creates the `Application`, registers the 3 scenes and runs. If `assets/` is missing, exits with a message saying to run the generator. |
| `scenes/menu.py`, `scenes/game.py`, `scenes/game_over.py` | The three scenes |
| `objects/bird.py`, `objects/pipes.py`, `objects/ground.py` | Reusable game objects |
| `save.py` | High score load/save to `save.json` (git-ignored) |

## Display and assets

- Pixel art drawn at 144×256 and scaled ×3 with nearest-neighbour, giving a **432×768 window**.
- **PNGs:** `bird.png` (3-frame spritesheet: wing up, mid, down), `pipe.png` (body with cap; the top pipe uses `flip_y`), `ground.png` (tileable), `background.png` (sky, clouds, city skyline), `title.png`, `get_ready.png`, `game_over.png`, `panel.png` (score panel), `medal_bronze.png`, `medal_silver.png`, `medal_gold.png`, `medal_platinum.png`, `new_badge.png`.
- **WAVs** (synthesised): `flap`, `point`, `hit`, `die`, `swoosh`.
- On-screen numbers and text use jazz's `Label` with the bundled font.

## Scene 1: Main menu

- Background, scrolling ground, and a `title.png` that bobs using a looping `Tween`.
- The bird is an `AnimatedSprite` that flaps and bobs.
- Shows "Best: N".
- **Play** and **Quit** `Button`s. Space or a click also starts the game (swoosh sound).

## Scene 2: Game

- **Get Ready phase:** the bird hovers with the `get_ready.png` prompt showing. The first flap starts the run.
- **Bird:** an `Area` with a circle collider and an `AnimatedSprite` child.
  - Gravity and velocity are integrated manually. Space, Up or left-click sets the upward velocity (flap sound).
  - The bird tilts nose-up while rising and dives nose-down as it falls.
- **Pipes:** each pair is two static `Body` rect colliders with pipe sprites, in a `Group`.
  - A repeating `create_timer` spawns a pair every ~1.5 s with a random gap height.
  - Pipes scroll left at a constant speed and `queue_kill` once they're off-screen.
- **Scoring:** a sensor `Area` sits in each gap. The bird's first overlap with it adds +1 and plays the point sound.
- **Death:** the bird's `Area.get_entered()` hits the pipe or ground `Group`, or the bird leaves the top of the screen. Then:
  - hit sound, white flash and `camera.add_shake`, and scrolling stops
  - the bird drops to the ground (die sound)
  - after ~1 s, the game moves to Game Over and passes the score through `on_unload`
- The score `Label` sits at the top centre. P or Esc pauses using `toggle_pause`.
- Fixed classic difficulty (no speed ramp).

## Scene 3: Game over

- `game_over.png` drops in, then the score panel slides up (`Tween`, `EASE_OUT_BACK`).
- The score counts up to the final value, then shows Best and a **NEW** badge if it's a new record.
- Medals: bronze ≥10, silver ≥20, gold ≥30, platinum ≥40.
- **Retry** (back to the game) and **Menu** buttons. Space also retries.
- The high score is saved here.

## Verification

- Run `generate_assets.py`, then `main.py` as a smoke test.
- A scripted run injects inputs and checks that all three scenes load, pipes spawn, and scoring and collision fire.
- A human playtest is still needed to judge the feel.
- Nothing in `jazz/` changes, so no `.changes` walkthrough or full test run is needed.
