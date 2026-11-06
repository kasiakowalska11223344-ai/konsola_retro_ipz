# sounds.py
import pygame
import math
from array import array


class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=1)

        self.waka_1 = self._make_sweep(260, 420, 0.07)
        self.waka_2 = self._make_sweep(420, 260, 0.07)
        self.waka_toggle = False

        self.power_sound = self._make_sweep(350, 750, 0.22)
        self.eat_ghost_sound = self._make_sweep(200, 950, 0.35)
        self.death_sound = self._make_sweep(600, 80, 0.65)

    def _make_sweep(self, start_freq, end_freq, duration, volume=0.15):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array('h')
        max_amp = int(32767 * volume)

        phase = 0.0
        for i in range(n_samples):
            progress = i / n_samples
            freq = start_freq + (end_freq - start_freq) * progress
            phase += 2 * math.pi * freq / sample_rate

            sample = max_amp if math.sin(phase) >= 0 else -max_amp
            buf.append(sample)

        return pygame.mixer.Sound(buffer=buf)

    def play_waka(self):
        if self.waka_toggle:
            self.waka_1.play()
        else:
            self.waka_2.play()
        self.waka_toggle = not self.waka_toggle

    def play_power(self):
        self.power_sound.play()

    def play_eat_ghost(self):
        self.eat_ghost_sound.play()

    def play_death(self):
        self.death_sound.play()