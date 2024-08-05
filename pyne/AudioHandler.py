import pygame

class AudioHandler:
    def __init__(self, sounds):
        self.sounds = sounds
        self.volume_sfx, self.volume_music = 0.5, 0.2
        self._music_channel = pygame.mixer.Channel(0)
        self._sfx_channel = pygame.mixer.Channel(1)
        self.set_volume_sfx(self.volume_sfx)
        self.set_volume_music(self.volume_music)

    def update_sounds(self, sounds):
        self.sounds.update(sounds)
    
    def set_volume_sfx(self, volume):
        self.volume_sfx = volume
        self.update_clips()

    def set_volume_sfx_relative(self, value):
        self.volume_sfx += value
        self.update_clips()
    
    def set_volume_music(self, volume):
        self.volume_music = volume
        self.update_clips()

    def set_volume_music_relative(self, value):
        self.volume_music += value
        self.update_clips()

    def update_clips(self):
        self._sfx_channel.set_volume(self.volume_sfx)
        self._music_channel.set_volume(self.volume_music)

    def play_song(self, name, loops=-1):
        if self._music_channel.get_busy():
            self._music_channel.stop()
        self._music_channel.play(self.sounds[name], loops)

    def play_sound(self, name):
        if self._sfx_channel.get_busy():
            self._sfx_channel.stop()
        self._sfx_channel.play(self.sounds[name])