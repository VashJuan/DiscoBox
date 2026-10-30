# SPDX-FileCopyrightText: 2026 John Cornelison for Vashon Software
# SPDX-License-Identifier: MIT

"""Generic theme: the year-round disco show"""

# Lights: animation names from lights.py, shown in random order
SHOW = (
    "rainbow",
    "rainbow comet",
    "rainbow chase columns",
    "rainbow chase pixels",
    "rainbow sparkle",
    "purple comet rows",
    "amber comet columns",
    "jade chase rows",
)
LIGHTNING = False  # flash the panel white as each chime starts

# Door squeak (creak.py)
SQUEAK_PITCH = (1250, 700)  # Hz, door closed .. fully open
SQUEAK_RASP = (18, 30)  # clicks per second, slow .. fast swing

# Chimes while the door is still: names from creak.CHIMES,
# or a 22050 Hz mono 16-bit WAV file in sounds/ (skipped if not on the board)
CHIMES = ("doorbell", "boing", "laser", "frog", "saucer")

# Slide whistle (whistle.py): wobble in octaves; 0 = a plain whistle
WHISTLE_VIBRATO = 0
# WAVs in sounds/ to play instead of the whistle (whistle.BeamSounds); () = the whistle
BEAM_SOUNDS = ()
