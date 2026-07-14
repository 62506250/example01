import numpy as np
import pygame


def make_tone(frequency, duration, volume=0.35, sample_rate=44100):
    """Builds a short sine-wave tone as a stereo array of sound samples."""
    sample_count = int(sample_rate * duration)
    t = np.linspace(0, duration, sample_count, endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)

    fade = np.linspace(1.0, 0.0, wave.size)
    wave = wave * fade * volume

    samples = (wave * 32767).astype(np.int16)
    stereo_samples = np.column_stack((samples, samples))
    return np.ascontiguousarray(stereo_samples)


class SoundManager:
    """Loads and plays every sound effect the game needs."""

    def __init__(self):
        self._enabled = False
        self._sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2)

            self._sounds["shoot"] = pygame.sndarray.make_sound(make_tone(180, 0.07, volume=0.25))
            self._sounds["hit"] = pygame.sndarray.make_sound(make_tone(760, 0.10, volume=0.35))
            self._sounds["powerup"] = pygame.sndarray.make_sound(make_tone(980, 0.16, volume=0.30))
            self._sounds["sabotage"] = pygame.sndarray.make_sound(make_tone(140, 0.22, volume=0.35))
            self._sounds["game_over"] = pygame.sndarray.make_sound(make_tone(520, 0.35, volume=0.30))
            self._enabled = True
        except Exception:
            self._enabled = False

    def _play(self, name):
        if not self._enabled:
            return
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def play_shoot(self):
        self._play("shoot")

    def play_hit(self):
        self._play("hit")

    def play_powerup(self):
        self._play("powerup")

    def play_sabotage(self):
        self._play("sabotage")

    def play_game_over(self):
        self._play("game_over")
