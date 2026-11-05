# SPDX-FileCopyrightText: 2023 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Disco Mailbox settings shared by all modules"""

# production: fast start-up, music first, no audio tests or debug printing
production = True
# production = False  # run the start-up audio tests & print debug information

verbose = not production  # print debug information to serial port

import os

# Seasonal theme: a file in themes/ (lights, door sound, chimes, whistle).
# tools/deploy.ps1 sets this on the board and puts that theme's songs in sounds/
theme = "generic"
theme_settings = getattr(__import__("themes." + theme), theme)

sound_dir = "sounds/"


def read_playlist():
    """Song file names, in order, from sounds/playlist.txt (written by
    tools/make_clips.py); every MP3 in sounds/ if there is no playlist"""
    try:
        with open(sound_dir + "playlist.txt") as playlist:
            names = [line.strip() for line in playlist]
        return [name for name in names if name and not name.startswith("#")]
    except OSError:
        return sorted(name for name in os.listdir(sound_dir) if name.endswith(".mp3"))


# 22050 Hz mono clips, to match the mixer (cut by tools/make_clips.py)
mp3files = read_playlist()

door_creak = True  # cartoon creak over the song as the door swings (creak.py)
slide_whistle = True  # tone that follows the distance sensor as mail moves (whistle.py)
music_lights = True  # panel brightness pulses with the song (lights.MusicPulse)

# Indoors for bench testing; outdoors needs more volume & brighter lights
outdoors = False
volume = 0.6 if outdoors else 0.4  # master volume for songs & effects (1 = full)
led_max = 0.75 if outdoors else 0.25  # panel brightness on the loudest beats

# Sensors can be switched off to chase stutters in the music (each I2C read
# takes time from the MP3 decoder). Off = never set up or polled.
distance_sensor = True  # VL53L1X: the slide whistle / beam sounds
accelerometer = True  # LIS3DH on the Prop-Maker: door creak & chimes
i2c_khz = 50  # I2C bus speed; slow (50) for the ~3 ft cable to the distance sensor, 100 normal

# Print any loop pass slower than this (ms) to the serial port, even in production
slow_tick_ms = 60
