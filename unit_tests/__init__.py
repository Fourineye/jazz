"""Jazz engine unit tests.

The SDL drivers are set here so every entry point (``run_tests.py`` or
``python -m unittest unit_tests.<module>``) runs headless. They must be set
before ``jazz`` is imported, because importing it calls ``pygame.init()``.
"""

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
