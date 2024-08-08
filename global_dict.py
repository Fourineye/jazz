from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import Application, Scene, InputHandler, Keyboard, Mouse, SoundManager
    from .utils import Surface


class Globals:
    app: 'Application' = None
    scene: type['Scene'] = None
    input: 'InputHandler' = None
    key: 'Keyboard' = None
    mouse: 'Mouse' = None
    display: 'Surface' = None
    sound: 'SoundManager' = None


SETTINGS = {"master_volume": 1.0, "music_volume": 1.0, "sound_volume": 1.0}
