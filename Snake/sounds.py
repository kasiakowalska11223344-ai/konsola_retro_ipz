"""Loading and playback of the game's sound effects."""

from pathlib import Path

import pygame

# Locate the sound files relative to this Python file
SOUND_DIRECTORY = Path(__file__).parent / "assets" / "sounds"


class SoundEffects:
    """Small wrapper around Pygame's mixer with graceful audio fallback."""

    def __init__(self):
        self.enabled = False

        self.turn = None
        self.eat_fruit = None
        self.game_over = None

        # Audio is optional: the game can still run without an audio device.
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=1,
                    buffer=512
                )

            # Load all three sound effects
            self.turn = pygame.mixer.Sound(
                str(SOUND_DIRECTORY / "turn.wav")
            )

            self.eat_fruit = pygame.mixer.Sound(
                str(SOUND_DIRECTORY / "eat_fruit.wav")
            )

            self.game_over = pygame.mixer.Sound(
                str(SOUND_DIRECTORY / "game_over.wav")
            )

            # Adjust individual sound volumes
            self.turn.set_volume(0.45)
            self.eat_fruit.set_volume(0.65)
            self.game_over.set_volume(0.7)

            self.enabled = True

        except (pygame.error, OSError) as error:
            print(f"Sound effects unavailable: {error}")

    def play_turn(self):
        """Play when a queued direction change is actually applied."""

        if self.enabled:
            self.turn.play()

    def play_eat_fruit(self):
        """Play when the snake eats a fruit."""

        if self.enabled:
            self.eat_fruit.play()

    def play_game_over(self):
        """Play when the player loses."""

        if self.enabled:
            self.game_over.play()
