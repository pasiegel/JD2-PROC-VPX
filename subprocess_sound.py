"""
subprocess_sound.py - SoundController that delegates to a python.exe subprocess.

pythonw.exe (the COM server) has Windows audio session issues that cause its
audio to be silenced. This routes all audio through python.exe which works correctly.
Drop-in replacement for procgame.sound.SoundController.
"""
import os
import subprocess
import logging

_PYTHON = r'C:\Python27\python.exe'
_SERVER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       r'..\..\tools\audio_server.py')


class _SoundProxy(object):
    """Mimics pygame.mixer.Sound just enough for jd2.stop_all_sounds()."""
    def __init__(self, controller, key):
        self._controller = controller
        self._key = key

    def stop(self):
        self._controller._send('stop\t%s' % self._key)


class SubprocessSoundController(object):
    """Routes pygame audio through a python.exe subprocess."""

    enabled = True

    def __init__(self, delegate):
        self.logger = logging.getLogger('game.sound')
        self.sounds = {}   # key -> [_SoundProxy]  (for jd2 compatibility)
        self.music  = {}   # key -> [path]
        self.music_volume_offset = 0
        self.volume = 0.5
        self.voice_end_time = 0   # kept for external access; server manages its own
        self._proc = None

        server_path = os.path.normpath(_SERVER)
        if not os.path.isfile(server_path):
            self.logger.error("audio_server.py not found at %s", server_path)
            self.enabled = False
            return

        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = 0  # SW_HIDE
            self._proc = subprocess.Popen(
                [_PYTHON, server_path],
                stdin=subprocess.PIPE,
                startupinfo=si,
            )
            self.logger.info("Audio subprocess started PID=%s", self._proc.pid)
        except Exception as e:
            self.logger.error("Failed to start audio subprocess: %s", e)
            self.enabled = False
            return

        self.set_volume(0.5)

    # ------------------------------------------------------------------
    def _send(self, line):
        if self._proc and self._proc.stdin:
            try:
                self._proc.stdin.write((line + '\n').encode('utf-8'))
                self._proc.stdin.flush()
            except Exception as e:
                self.logger.error("audio send error: %s", e)

    # ------------------------------------------------------------------
    def register_sound(self, key, sound_file):
        self.logger.info("Registering sound - key: %s, file: %s", key, sound_file)
        if not self.enabled:
            return
        if os.path.isfile(sound_file):
            if key not in self.sounds:
                self.sounds[key] = [_SoundProxy(self, key)]
            self._send('register_sound\t%s\t%s' % (key, sound_file))
        else:
            self.logger.error("Sound registration error: file %s does not exist!", sound_file)

    def register_music(self, key, music_file):
        if not self.enabled:
            return
        if os.path.isfile(music_file):
            self.music.setdefault(key, [])
            if music_file not in self.music[key]:
                self.music[key].append(music_file)
            self._send('register_music\t%s\t%s' % (key, music_file))
        else:
            self.logger.error("Music registration error: file %s does not exist!", music_file)

    # ------------------------------------------------------------------
    def play(self, key, loops=0, max_time=0, fade_ms=0):
        self.logger.info("play called: %s enabled=%s", key, self.enabled)
        if not self.enabled:
            return 0
        if key in self.sounds:
            self._send('play\t%s' % key)
            return 0
        else:
            self.logger.warning("play: key not found: %s", key)
            return 0

    def play_voice(self, key, loops=0, max_time=0, fade_ms=0):
        self.logger.info("play_voice called: %s enabled=%s", key, self.enabled)
        if not self.enabled:
            return 0
        if key in self.sounds:
            self._send('play_voice\t%s' % key)
            return 3.0  # approximate; server manages actual voice_end_time
        else:
            self.logger.warning("play_voice: key not found: %s", key)
            return 0

    def play_music(self, key, loops=0, start_time=0.0):
        if not self.enabled:
            return
        if key in self.music:
            self._send('play_music\t%s\t%d\t%f' % (key, loops, start_time))

    def stop_music(self):
        if not self.enabled:
            return
        self._send('stop_music')

    def fadeout_music(self, time_ms=450):
        if not self.enabled:
            return
        self._send('fadeout_music\t%d' % time_ms)

    def load_music(self, key):
        pass  # handled server-side inside play_music

    def stop(self, key, loops=0, max_time=0, fade_ms=0):
        if not self.enabled:
            return
        if key in self.sounds:
            self._send('stop\t%s' % key)

    def stop_all(self):
        """Send stop_all to server and reset voice timer."""
        self._send('stop_all')
        self.voice_end_time = 0

    # ------------------------------------------------------------------
    def set_volume(self, new_volume):
        self.volume = new_volume
        if not self.enabled:
            return
        self._send('set_volume\t%f\t%f' % (new_volume, self.music_volume_offset))

    def volume_up(self):
        if not self.enabled:
            return self.volume * 10
        if self.volume < 0.8:
            self.set_volume(self.volume + 0.1)
        return self.volume * 10

    def volume_down(self):
        if not self.enabled:
            return self.volume * 10
        if self.volume > 0.2:
            self.set_volume(self.volume - 0.1)
        return self.volume * 10

    def beep(self):
        pass
