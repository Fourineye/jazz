"""Flappy Bird built with the jazz engine.

Usage:
    uv run python examples/flappy/generate_assets.py   # once
    uv run python examples/flappy/main.py

Controls:
    Space / Up / left click   flap (Space also starts and retries)
    P / Esc                   pause
    F3                        toggle jazz debug rendering (colliders and object origins)
"""

import sys

from config import HEIGHT, WIDTH, assets_present


def main() -> None:
    """Registers the menu, game and game over scenes and runs the game."""
    if not assets_present():
        print("Assets not found. Run: uv run python examples/flappy/generate_assets.py")
        sys.exit(1)

    from jazz import Application
    from scenes.game import GameScene
    from scenes.game_over import GameOverScene
    from scenes.menu import MenuScene

    app = Application(WIDTH, HEIGHT, "Flappy Bird", vsync=True)
    app.add_scene(MenuScene)
    app.add_scene(GameScene)
    app.add_scene(GameOverScene)
    app.run()


if __name__ == "__main__":
    main()
