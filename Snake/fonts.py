from pathlib import Path
import pygame

FONT_PATH = (
        Path(__file__).resolve().parent
        / "assets"
        / "fonts"
        / "PressStart2P-Regular.ttf"
)


def load_game_font(size: int) -> pygame.font.Font:
    if not FONT_PATH.is_file():
        raise FileNotFoundError(
            "Copy PressStart2P-Regular.ttf into assets/fonts/"
        )

    return pygame.font.Font(str(FONT_PATH), size)
