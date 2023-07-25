# Engine
This project is to wrap pygame into a more conveinent format that handles some of the more common tasks in game development.

## #TODO
- Redo UI module
- Forever documentation
- Particle System (In Progress)
- Redo Animation system (In Progress)
- Light Map

# Basic Example Program
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

# Documentation
TODO