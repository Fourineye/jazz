"""Game scene: Get Ready, playing, and the death sequence."""

import random
from typing import Any

from jazz import Globals, Timer, Tween, EASE_OUT_QUADRATIC

from scenes.base import FlappyScene
from config import (
    GROUND_Y,
    PIPE_GAP,
    PIPE_GAP_MARGIN,
    PIPE_INTERVAL,
    SCROLL_SPEED,
    WIDTH,
    flap_pressed,
    play_sound,
)
from objects.bird import RADIUS, Bird
from objects.ground import Ground
from objects.pipes import PIPE_WIDTH, PipePair
from objects.ui import ShadowLabel, add_art, add_background, add_flash, bob

READY = "ready"
PLAYING = "playing"
DYING = "dying"
DONE = "done"

BIRD_START = (WIDTH * 0.3, 330)
FLOOR = GROUND_Y - RADIUS


class GameScene(FlappyScene):
    """The main game. The first flap starts the run; hitting a pipe, the ground or the ceiling ends it."""

    name = "game"

    def __init__(self) -> None:
        """Initializes the GameScene."""
        super().__init__()
        self.state: str = READY
        self.score: int = 0
        self.bird: Bird | None = None
        self.ground: Ground | None = None
        self.bob_tween: Tween | None = None
        self.get_ready = None
        self.paused_banner = None
        self.score_label: ShadowLabel | None = None
        self.flash = None
        self.spawn_timer: Timer | None = None
        # jazz's Group is broken (FINDINGS.md #1), so pipes are tracked in a plain list
        self.pipes: list[PipePair] = []

    def on_load(self, data: dict[Any, Any]) -> None:
        """Builds the level in its Get Ready state.

        Args:
            data (dict[Any, Any]): Data from the previous scene. Unused.
        """
        play_sound("swoosh")
        add_background(self)
        self.ground = self.add_object(Ground(solid=True))
        self.bird = self.add_object(Bird(pos=BIRD_START))
        self.bob_tween = self.add_object(bob(self.bird, amplitude=10, period=0.8))

        self.get_ready = add_art(self, "get_ready", (WIDTH / 2, 220))
        self.paused_banner = add_art(self, "paused", (WIDTH / 2, 300), visible=False)
        self.score_label = self.add_object(ShadowLabel(text="0", fontsize=64, pos=(WIDTH / 2, 80)))
        self.flash = add_flash(self)

    def on_unload(self) -> dict[Any, Any]:
        """Passes the final score to the game over scene.

        Returns:
            dict[Any, Any]: The score.
        """
        return {"score": self.score}

    def update(self, delta: float) -> None:
        """Runs the state machine.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        if self.state == PLAYING and (Globals.key.press("p") or Globals.key.press("escape")):
            self.toggle_pause()
            self.paused_banner.visible = self._paused
        if self._paused:
            return

        if self.state == READY:
            self.ground.scroll(SCROLL_SPEED * delta)
            if flap_pressed():
                self.start_run()
        elif self.state == PLAYING:
            self.update_playing(delta)
        elif self.state == DYING:
            if self.bird.fall(delta, FLOOR):
                self.state = DONE
                self.create_timer(1.0, self.end_game, ())

    def start_run(self) -> None:
        """Leaves Get Ready: stops the idle bob, starts pipe spawning and flaps."""
        self.state = PLAYING
        self.bob_tween.stop()
        self.bob_tween.queue_kill()
        self.get_ready.visible = False
        self.bird.flap()
        self.spawn_pipe()
        self.spawn_timer = self.add_object(Timer(PIPE_INTERVAL, self.spawn_pipe, one_shot=False))

    def update_playing(self, delta: float) -> None:
        """Moves the bird and pipes, then resolves what the bird is touching.

        Args:
            delta (float): Time in seconds since the last frame.
        """
        if flap_pressed():
            self.bird.flap()
        self.bird.fall(delta)

        scroll = SCROLL_SPEED * delta
        self.ground.scroll(scroll)
        for pipe in self.pipes:
            pipe.move((-scroll, 0))
        for pipe in [p for p in self.pipes if p.x < -PIPE_WIDTH]:
            self.pipes.remove(pipe)
            pipe.queue_kill()

        # Query after moving: the engine refreshes Area.entered before Scene.update
        # runs, so it would be a frame behind (see FINDINGS.md)
        for obj in self.bird.get_entered():
            kind = getattr(obj, "kind", None)
            if kind == "gate" and not obj.scored:
                obj.scored = True
                self.score += 1
                self.score_label.set_text(str(self.score))
                play_sound("point")
            elif kind in ("pipe", "ground"):
                self.crash(hit_ground=(kind == "ground"))
                return

        if self.bird.y < -RADIUS:
            self.crash(hit_ground=False)

    def spawn_pipe(self) -> None:
        """Spawns a pipe pair just off the right edge with a random gap height."""
        if self.state != PLAYING:
            return
        low = PIPE_GAP_MARGIN + PIPE_GAP / 2
        high = GROUND_Y - PIPE_GAP_MARGIN - PIPE_GAP / 2
        pipe = self.add_object(PipePair(WIDTH + PIPE_WIDTH, random.uniform(low, high)))
        self.pipes.append(pipe)

    def crash(self, hit_ground: bool) -> None:
        """Starts the death sequence: sound, flash, camera shake and the fall.

        Args:
            hit_ground (bool): True if the bird hit the ground, so there's no fall.
        """
        self.state = DYING
        self.bird.die()
        self.spawn_timer.queue_kill()
        play_sound("hit")
        if not hit_ground:
            self.create_timer(0.25, play_sound, ("die",))
            self.bird.velocity = max(self.bird.velocity, 0.0)
        self.camera.add_shake(0.8)

        self.flash.alpha = 255
        self.add_object(
            Tween(target_object=self.flash, target_property="alpha", target_value=0, time=0.35, easing=EASE_OUT_QUADRATIC, play=True)
        )

    def end_game(self) -> None:
        """Switches to the game over scene."""
        Globals.app.set_next_scene("game_over")
        self.stop()
