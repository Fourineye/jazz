"""Generates every image and sound asset used by the Flappy Bird example.

Images are drawn as low resolution pixel art (the game scales them x3 at runtime)
and written as PNGs. Sounds are synthesised and written as 16-bit mono WAVs.
This script only depends on pygame, not on jazz.

Usage:
    uv run python examples/flappy/generate_assets.py
"""

import math
import os
import random
import struct
import wave

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SAMPLE_RATE = 22050

# Palette
OUTLINE = (84, 56, 71)
WHITE = (255, 255, 255)
SKY = (78, 192, 202)
CLOUD = (234, 252, 219)
CLOUD_SHADE = (205, 238, 196)
CITY = (168, 222, 182)
CITY_WINDOW = (139, 204, 160)
BUSH = (94, 190, 74)
BUSH_DARK = (82, 168, 64)
GRASS_LIGHT = (156, 230, 89)
GRASS_DARK = (115, 191, 46)
GRASS_EDGE = (84, 128, 50)
DIRT = (222, 216, 149)
DIRT_DARK = (207, 196, 124)
PIPE_LIGHT = (156, 230, 89)
PIPE_MID = (115, 191, 46)
PIPE_DARK = (84, 128, 50)
YELLOW = (250, 200, 50)
YELLOW_LIGHT = (253, 234, 120)
ORANGE = (240, 110, 40)
RED = (230, 70, 50)
PANEL = (222, 216, 149)
PANEL_LIGHT = (240, 236, 190)
PANEL_TEXT = (230, 116, 80)
BUTTON = (240, 140, 50)
BUTTON_HOVER = (250, 170, 80)
BUTTON_PRESSED = (210, 110, 40)

# 5x7 bitmap font. Each glyph is 7 rows of 5 characters, "#" is a filled pixel.
FONT = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ### ", "#   #", "#    ", "#    ", "#    ", "#   #", " ### "],
    "D": ["#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ### ", "#   #", "#    ", "# ###", "#   #", "#   #", " ####"],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "/": ["    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "],
    "!": ["  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "],
    " ": ["     "] * 7,
}


def text_mask(text: str, px: int = 1, spacing: int = 1) -> pygame.Surface:
    """Renders text with the bitmap font as a white-on-transparent mask.

    Args:
        text (str): Text to render. Must only use characters in FONT.
        px (int, optional): Size of one font pixel in image pixels. Defaults to 1.
        spacing (int, optional): Gap between glyphs in font pixels. Defaults to 1.

    Returns:
        pygame.Surface: The rendered text mask.
    """
    width = (len(text) * (5 + spacing) - spacing) * px
    surf = pygame.Surface((width, 7 * px), pygame.SRCALPHA)
    for i, char in enumerate(text):
        glyph = FONT[char]
        x0 = i * (5 + spacing) * px
        for y, row in enumerate(glyph):
            for x, cell in enumerate(row):
                if cell == "#":
                    surf.fill(WHITE, (x0 + x * px, y * px, px, px))
    return surf


def tinted(mask: pygame.Surface, color: tuple[int, int, int]) -> pygame.Surface:
    """Returns a copy of a white mask recoloured to the given colour.

    Args:
        mask (pygame.Surface): White-on-transparent mask.
        color (tuple[int, int, int]): The new colour.

    Returns:
        pygame.Surface: The recoloured surface.
    """
    surf = mask.copy()
    surf.fill(color + (255,), special_flags=pygame.BLEND_RGBA_MULT)
    return surf


def outlined_text(text: str, color: tuple[int, int, int], px: int = 1, shadow: bool = True) -> pygame.Surface:
    """Renders bitmap text with a 1px dark outline and an optional drop shadow.

    Args:
        text (str): Text to render.
        color (tuple[int, int, int]): Fill colour of the text.
        px (int, optional): Size of one font pixel in image pixels. Defaults to 1.
        shadow (bool, optional): Adds a dark shadow offset down-right. Defaults to True.

    Returns:
        pygame.Surface: The rendered text.
    """
    mask = text_mask(text, px)
    pad = 2
    surf = pygame.Surface((mask.get_width() + pad * 2 + 1, mask.get_height() + pad * 2 + 1), pygame.SRCALPHA)
    dark = tinted(mask, OUTLINE)
    if shadow:
        for dx in range(-1, 3):
            for dy in range(-1, 3):
                surf.blit(dark, (pad + dx, pad + dy))
    else:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                surf.blit(dark, (pad + dx, pad + dy))
    surf.blit(tinted(mask, color), (pad, pad))
    return surf


def save(surf: pygame.Surface, name: str) -> None:
    """Writes a surface to the asset folder as a PNG.

    Args:
        surf (pygame.Surface): Surface to save.
        name (str): File name, without extension.
    """
    pygame.image.save(surf, os.path.join(ASSET_DIR, f"{name}.png"))


# ---------------------------------------------------------------- images


def make_background() -> None:
    """Sky, clouds, city skyline and bushes. 144x256; the ground covers the bottom 40px."""
    surf = pygame.Surface((144, 256))
    surf.fill(SKY)
    rng = random.Random(7)

    # Cloud band made of overlapping circles
    for x in range(-8, 152, 12):
        r = rng.randint(8, 13)
        pygame.draw.circle(surf, CLOUD_SHADE, (x, 168 - r // 2), r)
    for x in range(-4, 152, 12):
        r = rng.randint(6, 10)
        pygame.draw.circle(surf, CLOUD, (x, 170 - r // 2), r)
    surf.fill(CLOUD, (0, 168, 144, 20))

    # City skyline
    x = 0
    while x < 144:
        w = rng.randint(8, 14)
        h = rng.randint(14, 30)
        top = 196 - h
        surf.fill(CITY, (x, top, w, h))
        for wy in range(top + 3, 192, 4):
            for wx in range(x + 2, x + w - 2, 3):
                surf.fill(CITY_WINDOW, (wx, wy, 1, 2))
        x += w + rng.randint(0, 2)

    # Bushes
    for x in range(-6, 152, 9):
        r = rng.randint(6, 9)
        pygame.draw.circle(surf, BUSH_DARK, (x, 206), r + 1)
    for x in range(-2, 152, 9):
        r = rng.randint(5, 8)
        pygame.draw.circle(surf, BUSH, (x, 207), r)
    surf.fill(BUSH, (0, 204, 144, 12))
    save(surf, "background")


def make_ground() -> None:
    """Tileable ground strip, 168x40. The stripe pattern repeats every 12px."""
    surf = pygame.Surface((168, 40))
    surf.fill(DIRT)
    surf.fill(GRASS_EDGE, (0, 0, 168, 1))
    # Diagonal grass stripes, period 12
    for x in range(-12, 180):
        for y in range(1, 7):
            light = ((x + y) // 6) % 2 == 0
            if 0 <= x < 168:
                surf.set_at((x, y), GRASS_LIGHT if light else GRASS_DARK)
    surf.fill(GRASS_EDGE, (0, 7, 168, 1))
    surf.fill(DIRT_DARK, (0, 8, 168, 2))
    # Dirt speckles on a 12px period so the strip still tiles
    for x0 in range(0, 168, 12):
        for dx, dy in ((2, 16), (7, 22), (4, 29), (10, 34), (1, 37)):
            surf.fill(DIRT_DARK, (x0 + dx, dy, 2, 1))
    save(surf, "ground")


def make_bird() -> None:
    """3-frame bird spritesheet, 19x14 per cell (17x12 art plus a 1px border): wing up, mid, down."""
    frames = []
    wing_rows = {0: 3, 1: 5, 2: 7}
    for frame in range(3):
        f = pygame.Surface((17, 12), pygame.SRCALPHA)
        # Body
        pygame.draw.ellipse(f, OUTLINE, (0, 0, 15, 12))
        pygame.draw.ellipse(f, YELLOW, (1, 1, 13, 10))
        pygame.draw.ellipse(f, YELLOW_LIGHT, (3, 1, 8, 4))
        # Eye
        pygame.draw.ellipse(f, OUTLINE, (8, 0, 7, 7))
        pygame.draw.ellipse(f, WHITE, (9, 1, 5, 5))
        f.fill(OUTLINE, (12, 2, 1, 3))
        # Beak
        f.fill(OUTLINE, (10, 6, 7, 5))
        f.fill(ORANGE, (11, 7, 6, 1))
        f.fill(OUTLINE, (11, 8, 6, 1))
        f.fill(ORANGE, (11, 9, 5, 1))
        # Wing
        wy = wing_rows[frame]
        pygame.draw.ellipse(f, OUTLINE, (0, wy - 1, 8, 5))
        pygame.draw.ellipse(f, WHITE if frame != 1 else YELLOW_LIGHT, (1, wy, 6, 3))
        frames.append(f)
    # Each 17x12 frame sits in a 19x14 cell with a 1px transparent border, so
    # rotated frames can't sample pixels from their neighbours (FINDINGS.md #4)
    sheet = pygame.Surface((57, 14), pygame.SRCALPHA)
    for i, f in enumerate(frames):
        sheet.blit(f, (i * 19 + 1, 1))
    save(sheet, "bird")


def make_pipe() -> None:
    """Pipe with its cap on top, 26x160. The body is the centre 24 columns."""
    surf = pygame.Surface((26, 160), pygame.SRCALPHA)

    def shade_columns(x0: int, width: int, y0: int, height: int) -> None:
        for i in range(width):
            t = i / max(1, width - 1)
            if t < 0.15:
                col = PIPE_MID
            elif t < 0.45:
                col = PIPE_LIGHT
            elif t < 0.8:
                col = PIPE_MID
            else:
                col = PIPE_DARK
            surf.fill(col, (x0 + i, y0, 1, height))

    # Body
    surf.fill(OUTLINE, (1, 12, 24, 148))
    shade_columns(2, 22, 12, 148)
    # Cap
    surf.fill(OUTLINE, (0, 0, 26, 12))
    shade_columns(1, 24, 1, 10)
    surf.fill(PIPE_DARK, (1, 9, 24, 2))
    save(surf, "pipe")


def make_text_images() -> None:
    """Title, Get Ready and Game Over banners."""
    title = outlined_text("FLAPPY BIRD", WHITE, px=2)
    save(title, "title")

    ready_text = outlined_text("GET READY!", (120, 220, 90), px=2)
    hint = outlined_text("SPACE / CLICK", WHITE, px=1, shadow=False)
    w = max(ready_text.get_width(), hint.get_width())
    ready = pygame.Surface((w, ready_text.get_height() + hint.get_height() + 6), pygame.SRCALPHA)
    ready.blit(ready_text, ((w - ready_text.get_width()) // 2, 0))
    ready.blit(hint, ((w - hint.get_width()) // 2, ready_text.get_height() + 6))
    save(ready, "get_ready")

    save(outlined_text("GAME OVER", (250, 150, 60), px=2), "game_over")
    save(outlined_text("PAUSED", WHITE, px=2), "paused")


def make_panel() -> None:
    """Score panel, 113x57, with MEDAL / SCORE / BEST captions."""
    surf = pygame.Surface((113, 57), pygame.SRCALPHA)
    pygame.draw.rect(surf, OUTLINE, (0, 0, 113, 57), border_radius=3)
    pygame.draw.rect(surf, PANEL_LIGHT, (1, 1, 111, 55), border_radius=3)
    pygame.draw.rect(surf, PANEL, (2, 2, 109, 53), border_radius=2)
    # Medal slot
    pygame.draw.circle(surf, DIRT_DARK, (24, 34), 12)
    surf.blit(tinted(text_mask("MEDAL"), PANEL_TEXT), (10, 6))
    surf.blit(tinted(text_mask("SCORE"), PANEL_TEXT), (76, 6))
    surf.blit(tinted(text_mask("BEST"), PANEL_TEXT), (82, 30))
    save(surf, "panel")


def make_medals() -> None:
    """Bronze, silver, gold and platinum medals, 22x22 each."""
    colors = {
        "bronze": ((200, 120, 60), (230, 160, 100)),
        "silver": ((180, 180, 190), (230, 230, 240)),
        "gold": ((230, 180, 40), (255, 225, 110)),
        "platinum": ((200, 225, 230), (250, 255, 255)),
    }
    for name, (base, light) in colors.items():
        surf = pygame.Surface((22, 22), pygame.SRCALPHA)
        pygame.draw.circle(surf, OUTLINE, (11, 11), 11)
        pygame.draw.circle(surf, base, (11, 11), 10)
        pygame.draw.circle(surf, light, (11, 11), 7)
        pygame.draw.circle(surf, base, (11, 11), 5)
        # Five-point star
        points = []
        for i in range(10):
            r = 4.5 if i % 2 == 0 else 2
            a = -math.pi / 2 + i * math.pi / 5
            points.append((11 + r * math.cos(a), 11 + r * math.sin(a)))
        pygame.draw.polygon(surf, light, points)
        # Shine
        surf.fill(WHITE, (6, 5, 2, 1))
        surf.fill(WHITE, (5, 6, 1, 2))
        save(surf, f"medal_{name}")


def make_new_badge() -> None:
    """Red NEW badge, 21x11."""
    surf = pygame.Surface((21, 11), pygame.SRCALPHA)
    pygame.draw.rect(surf, RED, (0, 0, 21, 11), border_radius=2)
    surf.blit(text_mask("NEW", spacing=1), (2, 2))
    save(surf, "new_badge")


def make_buttons() -> None:
    """PLAY, QUIT, RETRY and MENU buttons, 40x16, in normal, hover and pressed states."""
    for label in ("PLAY", "QUIT", "RETRY", "MENU"):
        text = text_mask(label)
        for state, color in (("", BUTTON), ("_hover", BUTTON_HOVER), ("_pressed", BUTTON_PRESSED)):
            surf = pygame.Surface((40, 16), pygame.SRCALPHA)
            press = 1 if state == "_pressed" else 0
            if not press:
                pygame.draw.rect(surf, OUTLINE, (0, 2, 40, 14), border_radius=2)
            pygame.draw.rect(surf, OUTLINE, (0, press, 40, 14), border_radius=2)
            pygame.draw.rect(surf, WHITE, (1, 1 + press, 38, 12), border_radius=2)
            pygame.draw.rect(surf, color, (2, 2 + press, 36, 10), border_radius=1)
            tx = (40 - text.get_width()) // 2
            surf.blit(tinted(text, OUTLINE), (tx + 1, 4 + press))
            surf.blit(text, (tx, 3 + press))
            save(surf, f"button_{label.lower()}{state}")


def make_white() -> None:
    """1x1 white pixel with an alpha channel, used for the hit flash."""
    surf = pygame.Surface((1, 1), pygame.SRCALPHA)
    surf.fill((255, 255, 255, 255))
    save(surf, "white")


# ---------------------------------------------------------------- sounds


def write_wav(name: str, samples: list[float]) -> None:
    """Writes mono float samples in [-1, 1] as a 16-bit WAV.

    Args:
        name (str): File name, without extension.
        samples (list[float]): Audio samples.
    """
    path = os.path.join(ASSET_DIR, f"{name}.wav")
    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples
        )
        wav.writeframes(frames)


def sweep(f0: float, f1: float, duration: float, wave_fn, volume: float = 0.5, decay: float = 3.0) -> list[float]:
    """Frequency sweep with an exponential decay envelope.

    Args:
        f0 (float): Start frequency in Hz.
        f1 (float): End frequency in Hz.
        duration (float): Length in seconds.
        wave_fn (Callable[[float], float]): Maps phase (in cycles) to a sample in [-1, 1].
        volume (float, optional): Peak amplitude. Defaults to 0.5.
        decay (float, optional): Envelope decay rate. Defaults to 3.0.

    Returns:
        list[float]: Generated samples.
    """
    n = int(duration * SAMPLE_RATE)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / n
        freq = f0 + (f1 - f0) * t
        phase += freq / SAMPLE_RATE
        attack = min(1.0, i / (0.005 * SAMPLE_RATE))
        out.append(wave_fn(phase) * volume * attack * math.exp(-decay * t))
    return out


def sine(phase: float) -> float:
    return math.sin(2 * math.pi * phase)


def square(phase: float) -> float:
    return 1.0 if (phase % 1.0) < 0.5 else -1.0


def triangle(phase: float) -> float:
    return 4 * abs((phase % 1.0) - 0.5) - 1


def make_sounds() -> None:
    """Flap, point, hit, die and swoosh sound effects."""
    rng = random.Random(3)

    write_wav("flap", sweep(350, 900, 0.11, square, volume=0.18, decay=4))

    point = sweep(988, 988, 0.07, square, volume=0.15, decay=0.5)
    point += sweep(1319, 1319, 0.28, square, volume=0.15, decay=5)
    write_wav("point", point)

    n = int(0.18 * SAMPLE_RATE)
    hit = []
    for i in range(n):
        t = i / n
        noise = rng.uniform(-1, 1) * math.exp(-10 * t)
        thump = math.sin(2 * math.pi * 110 * i / SAMPLE_RATE) * math.exp(-6 * t)
        hit.append((noise * 0.5 + thump * 0.6) * 0.8)
    write_wav("hit", hit)

    write_wav("die", sweep(750, 120, 0.55, triangle, volume=0.4, decay=1.5))

    n = int(0.35 * SAMPLE_RATE)
    swoosh = []
    smooth = 0.0
    for i in range(n):
        t = i / n
        env = math.sin(math.pi * t) ** 2
        cutoff = 0.05 + 0.25 * t
        smooth += (rng.uniform(-1, 1) - smooth) * cutoff
        swoosh.append(smooth * env * 1.2)
    write_wav("swoosh", swoosh)


def main() -> None:
    """Generates every asset into the assets folder."""
    os.makedirs(ASSET_DIR, exist_ok=True)
    make_background()
    make_ground()
    make_bird()
    make_pipe()
    make_text_images()
    make_panel()
    make_medals()
    make_new_badge()
    make_buttons()
    make_white()
    make_sounds()
    print(f"Assets written to {ASSET_DIR}")


if __name__ == "__main__":
    main()
