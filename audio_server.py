"""
audio_server.py - JD P-ROC audio subprocess server.
Runs as python.exe (not pythonw.exe) so Windows audio sessions work correctly.
Reads tab-delimited commands from stdin, plays audio via pygame.
"""
import sys
import os
import random
import time

try:
    from pygame import mixer
    mixer.pre_init(44100, -16, 2, 1024)
    mixer.init()
except Exception as e:
    sys.stderr.write("audio_server: mixer init failed: %s\n" % e)
    sys.exit(1)

sounds = {}   # key -> [Sound, ...]
music  = {}   # key -> [path, ...]
volume = 0.5
music_volume_offset = 0.0
voice_end_time = 0.0

mixer.music.set_volume(volume)

for line in iter(sys.stdin.readline, ''):
    line = line.rstrip('\r\n')
    if not line:
        continue
    parts = line.split('\t')
    cmd   = parts[0]
    try:
        if cmd == 'register_sound':
            key, path = parts[1], parts[2]
            snd = mixer.Sound(str(path))
            snd.set_volume(volume)
            if key not in sounds:
                sounds[key] = [snd]
            else:
                sounds[key].append(snd)

        elif cmd == 'register_music':
            key, path = parts[1], parts[2]
            if key not in music:
                music[key] = [path]
            else:
                music[key].append(path)

        elif cmd == 'play':
            key = parts[1]
            if key in sounds and sounds[key]:
                random.shuffle(sounds[key])
                sounds[key][0].play()

        elif cmd == 'play_voice':
            key = parts[1]
            t = time.time()
            if t >= voice_end_time and key in sounds and sounds[key]:
                random.shuffle(sounds[key])
                sounds[key][0].play()
                voice_end_time = t + sounds[key][0].get_length()

        elif cmd == 'reset_voice':
            voice_end_time = 0.0

        elif cmd == 'play_music':
            key  = parts[1]
            loops = int(parts[2]) if len(parts) > 2 else 0
            start = float(parts[3]) if len(parts) > 3 else 0.0
            if key in music and music[key]:
                random.shuffle(music[key])
                mixer.music.load(music[key][0])
                mixer.music.play(loops, start)

        elif cmd == 'stop_music':
            mixer.music.stop()

        elif cmd == 'fadeout_music':
            ms = int(parts[1]) if len(parts) > 1 else 450
            mixer.music.fadeout(ms)

        elif cmd == 'stop':
            key = parts[1]
            if key in sounds and sounds[key]:
                sounds[key][0].stop()

        elif cmd == 'stop_all':
            for k in sounds:
                for s in sounds[k]:
                    try:
                        s.stop()
                    except:
                        pass
            voice_end_time = 0.0

        elif cmd == 'set_volume':
            volume = float(parts[1])
            offset = float(parts[2]) if len(parts) > 2 else 0.0
            music_volume_offset = offset
            mixer.music.set_volume(volume + offset)
            for k in sounds:
                for s in sounds[k]:
                    s.set_volume(volume)

        elif cmd == 'quit':
            break

    except Exception as e:
        sys.stderr.write("audio_server error [%s]: %s\n" % (cmd, e))

try:
    mixer.quit()
except:
    pass
