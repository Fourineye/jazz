import pygame.mixer as mix

from .. import SETTINGS
from ..utils import clamp, save_ini

music = mix.music


class SoundManager:
    """Manages music and sound effect playback, caching, and volumes."""

    def __init__(self) -> None:
        """Initializes the SoundManager with default volumes and empty sound cache."""
        self._sounds = {}
        self._master_volume = 1.0
        self._volume_m = 1.0
        self._volume_s = 1.0
        self._music_start = 0

    def save_to_ini(self) -> None:
        """Saves current sound manager volumes to the global INI settings."""
        SETTINGS["AUDIO"]["master_volume"] = self._master_volume
        SETTINGS["AUDIO"]["music_volume"] = self._volume_m
        SETTINGS["AUDIO"]["sound_volume"] = self._volume_s
        save_ini()

    def load_settings(self, settings: dict | None = None) -> None:
        """Loads and applies sound manager volumes from settings dictionary or global settings.

        Args:
            settings (dict, optional): Volume settings dict. Defaults to None (uses global SETTINGS["AUDIO"]).
        """
        if settings is None:
            settings = SETTINGS.get("AUDIO", {})
        self._volume_m = float(settings.get("music_volume", 1.0))
        self._volume_s = float(settings.get("sound_volume", 1.0))
        self.set_master_volume(settings.get("master_volume", 1.0))

    def set_master_volume(self, volume: float | str) -> None:
        """Sets the master volume and updates active music and sound volumes.

        Args:
            volume (float | str): Master volume factor between 0.0 and 1.0.
        """
        self._master_volume = clamp(float(volume), 0.0, 1.0)
        music.set_volume(self._volume_m * self._master_volume)
        for sound in self._sounds:
            sound.set_volume(self._volume_s * self._master_volume)

    def play_music(self, file: str | None = None, loops: int = 0, start: float = 0.0, fade_ms: int = 0) -> None:
        """Plays music tracks.

        Args:
            file (str, optional): The file path of the music track to load. Defaults to None.
            loops (int, optional): Number of times to loop the music. Defaults to 0 (loops once).
            start (float, optional): The starting position in seconds. Defaults to 0.0.
            fade_ms (int, optional): Fade-in time in milliseconds. Defaults to 0.
        """
        if file is not None:
            music.load(file)
        self._music_start = int(start * 1000)
        music.play(loops, start, fade_ms)

    def clear_music(self) -> None:
        """Unloads the currently loaded music track from the mixer."""
        music.unload()

    def queue_music(self, file: str, loops: int = 0) -> None:
        """Queues a music track to play immediately after the current one finishes.

        Args:
            file (str): The file path of the music track.
            loops (int, optional): Number of times to loop. Defaults to 0.
        """
        music.queue(file, loops=loops)

    def stop_music(self) -> None:
        """Stops active music playback."""
        music.stop()
        self._music_start = 0

    def pause_music(self) -> None:
        """Pauses active music playback."""
        music.pause()

    def resume_music(self) -> None:
        """Resumes paused music playback."""
        music.unpause()

    def set_music_pos(self, time: float) -> None:
        """Sets the absolute position of the music playback.

        Args:
            time (float): Position in seconds.
        """
        status = music.get_busy()
        # music.pause()
        if status:
            self.play_music(start=time)
        else:
            music.set_pos(time)
            self._music_start = int(time * 1000)

    def get_music_pos(self) -> int:
        """Returns the time music has been playing in milliseconds.

        Returns:
            int: Elapsed music playback time in milliseconds.
        """
        return self._music_start + music.get_pos()

    def fadeout_music(self, time: int) -> None:
        """Fades out and stops active music playback over a duration.

        Args:
            time (int): Fade out time in milliseconds.
        """
        music.fadeout(time)

    def get_music_playing(self) -> bool:
        """Checks if music is currently playing.

        Returns:
            bool: True if music is playing, otherwise False.
        """
        return music.get_busy()

    def set_music_volume(self, volume: float) -> None:
        """Sets the music volume factor.

        Args:
            volume (float): Volume factor between 0.0 and 1.0.
        """
        self._volume_m = clamp(volume, 0.0, 1.0)
        music.set_volume(self._volume_m * self._master_volume)

    def load_sound(self, file: str) -> mix.Sound:
        """Loads and caches a sound effect from the filesystem.

        Args:
            file (str): File path of the sound effect.

        Returns:
            Sound: The cached or loaded Pygame Sound object.
        """
        sound = self._sounds.get(file, None)
        if sound is None:
            sound = mix.Sound(file)
            self._sounds[file] = sound
        return sound

    def clear_sounds(self) -> None:
        """Stops and clears all cached sound effects."""
        for sound in self._sounds.values():
            sound.stop()
        self._sounds = {}

    def play_sound(self, file: str, loops: int = 0, maxtime: int = 0, fade_ms: int = 0) -> None:
        """Plays a sound effect.

        Args:
            file (str): File path of the sound effect.
            loops (int, optional): Number of loops to play. Defaults to 0.
            maxtime (int, optional): Maximum playback time in milliseconds. Defaults to 0.
            fade_ms (int, optional): Fade-in time in milliseconds. Defaults to 0.
        """
        sound = self.load_sound(file)
        sound.set_volume(self._volume_s * self._master_volume)
        sound.play(loops, maxtime, fade_ms)

    def set_sound_volume(self, volume: float) -> None:
        """Sets the sound effects volume factor.

        Args:
            volume (float): Volume factor between 0.0 and 1.0.
        """
        self._volume_s = clamp(volume, 0.0, 1.0)
        for sound in self._sounds:
            sound.set_volume(self._volume_s * self._master_volume)
