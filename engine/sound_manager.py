import pygame.mixer as mix

from ..utils import clamp, save_ini

music = mix.music

from ..global_dict import GAME_GLOBALS, SETTINGS


class SoundManager:
    def __init__(self):
        self._sounds = {}
        self._master_volume = 1.0
        self._volume_m = 1.0
        self._volume_s = 1.0

    def save_to_ini(self):
        SETTINGS["master_volume"] = self._master_volume
        SETTINGS["music_volume"] = self._volume_m
        SETTINGS["sound_volume"] = self._volume_s
        save_ini()

    def load_settings(self):
        self._volume_m = SETTINGS["music_volume"]
        self._volume_s = SETTINGS["sound_volume"]
        self.set_master_volume(SETTINGS["master_volume"])

    def set_master_volume(self, volume):
        self._master_volume = clamp(volume, 0.0, 1.0)
        music.set_volume(self._volume_m * self._master_volume)
        for sound in self._sounds:
            sound.set_volume(self._volume_s * self._master_volume)

    def play_music(self, file=None, loops=0, start=0.0, fade_ms=0):
        if file is not None:
            music.load(file)
        music.play(loops, start, fade_ms)

    def queue_music(self, file, loops=0):
        music.queue(file, loops=loops)

    def stop_music(self):
        music.stop()

    def pause_music(self):
        music.pause()

    def resume_music(self):
        music.unpause()

    def fadeout_music(self, time):
        music.fadeout(time)

    def set_music_volume(self, volume):
        self._volume_m = clamp(volume, 0.0, 1.0)
        music.set_volume(self._volume_m * self._master_volume)

    def load_sound(self, file) -> mix.Sound:
        sound = self._sounds.get(file, None)
        if sound is None:
            sound = mix.Sound(file)
            self._sounds[file] = sound
        return sound

    def clear_sounds(self):
        for sound in self._sounds.values():
            sound.stop()
        self._sounds = {}

    def play_sound(self, file, loops=0, maxtime=0, fade_ms=0):
        sound = self.load_sound(file)
        sound.set_volume(self._volume_s * self._master_volume)
        sound.play(loops, maxtime, fade_ms)

    def set_sound_volume(self, volume):
        self._volume_s = clamp(volume, 0.0, 1.0)
        for sound in self._sounds:
            sound.set_volume(self._volume_s * self._master_volume)
