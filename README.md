# Engine
This project is to wrap pygame into a more conveinent format that handles some of the more common tasks in game development.

## #TODO
- Redo UI module
- Forever documentation
- Particle System (In Progress)
- Light Map
- Redo Animation system (In Progress)

# Basic Example Program
```py
import Jazz


class Player(Jazz.GameObject):
    def __init__(self, **kwargs):
        kwargs.setdefault("name", "Player")
        super().__init__(**kwargs)
        self.add_child(Jazz.Sprite())

    def update(self, delta: float):
        movement = Jazz.Vec2()
        if Jazz.Game_Globals["Key"].held("up"):
            movement.y -= 1
        if Jazz.Game_Globals["Key"].held("down"):
            movement.y += 1
        if Jazz.Game_Globals["Key"].held("left"):
            movement.x -= 1
        if Jazz.Game_Globals["Key"].held("right"):
            movement.x += 1

        self.move(movement * 100 * delta)

class MainScene(Jazz.Scene):
    name = "Main"
    def on_load(self, data):
        self.add_object(Player(pos=(100, 100)), "player")

    def update(self, delta: float):
        Jazz.Game_Globals["App"].set_caption(self.player.pos)

if __name__ == "__main__":
    app = Jazz.Application(800, 600)
    app.add_scene(MainScene)
    app.run()

```

# Documentation
TODO