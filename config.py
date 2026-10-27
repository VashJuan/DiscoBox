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
